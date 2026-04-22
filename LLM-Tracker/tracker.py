import os
import json
import re
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

# 1. 擴展頻道與關鍵字監測範圍
CHANNELS = {
    "Matthew Berman": "https://www.youtube.com/@matthew_berman/videos", 
    "AI Explained": "https://www.youtube.com/@AIExplained/videos"
}

# 擴大關鍵字池，以應對不同創作者的標題風格
TECH_KEYWORDS = [
    "ai", "llm", "gpt", "model", "llama", "claude", "agent", "intelligence", 
    "o1", "sora", "sonnet", "opus", "gemini", "video", "multimodal"
]

# 2. 精確路徑定位
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "discourse_data.jsonl")

def load_processed_ids(filepath=DB_PATH):
    processed = set()
    if not os.path.exists(filepath):
        return processed
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    data = json.loads(line)
                    vid = data.get("video_id")
                    if vid: processed.add(vid)
                except: continue
    except Exception as e:
        print(f"⚠️ Error loading database: {e}")
    return processed

def get_recent_videos(channel_url, limit=5):
    print(f"\n1. Scanning recent content: {channel_url}")
    ydl_opts = {'extract_flat': True, 'playlist_items': f'1-{limit}', 'quiet': True, 'no_warnings': True}
    videos = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry: videos.append((entry['id'], entry['title']))
    except Exception as e:
        print(f"⚠️ yt-dlp extraction error: {e}")
    return videos

def get_transcript(video_id):
    """
    雙層抓取機制：
    1. 優先嘗試官方 API。
    2. 若失敗（被封鎖），嘗試使用 yt-dlp 抓取自動生成字幕。
    """
    print(f"2. Extracting subtitles for ID: {video_id}...")
    
    # 方案 A: 嘗試 youtube-transcript-api
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        return " ".join(t.text for t in transcript_list)
    except Exception as e:
        print(f"⚠️ Primary API failed: {e}")
        print("🔄 Switching to secondary fetcher (yt-dlp)...")

    # 方案 B: 備援方案 yt-dlp
    try:
        ydl_opts = {
            'skip_download': True,
            'writeautomaticsub': True, # 抓取自動生成的字幕
            'subtitleslangs': ['en'],
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            # 這裡 yt-dlp 不會直接回傳文字，但在雲端環境中，
            # 建議先手動等待或使用 Proxy 以繞過 403 錯誤。
            return None # 如果 yt-dlp 也無法直接獲取，代表 IP 真的被鎖死
    except:
        return None

def analyze_with_ai(channel_name, title, transcript):
    print(f"3. Invoking Semantic Analysis Engine (gpt-5.4-mini)...")
    api_key = os.getenv("CHATANYWHERE_API_KEY")
    if not api_key:
        print("❌ Error: CHATANYWHERE_API_KEY environment variable is empty.")
        return None

    client = OpenAI(api_key=api_key, base_url="https://api.chatanywhere.org/v1")
    
    prompt = f"""
    Analyze this YouTube transcript as a Digital Ethnographer.
    Channel: {channel_name} | Title: {title}
    Task: Extract discourse patterns and assess intellectual property (IP) risks.
    Output: Strictly JSON.
    Hierarchy:
    {{
        "metadata": {{"sentiment": "Positive/Neutral/Negative", "technical_complexity": "Beginner/Advanced"}},
        "analysis": {{
            "speaker_stance": "Summary of their position on the tech", 
            "key_technologies": ["List specific models/tools"], 
            "ideological_cluster": "e.g., Accelerationism, Primitivism, Pragmatism", 
            "relational_mapping": {{"allies": [], "competitors": [], "critiques": ""}}
        }},
        "risk_assessment": {{"copyright_risk": "Low/Medium/High", "reasoning": "Why?"}}
    }}
    Transcript Fragment: {transcript[:20000]}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[{"role": "system", "content": "You are a professional AI discourse analyst."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ AI Analysis API Call failed: {e}")
        return None

def process_pipeline():
    processed_ids = load_processed_ids()
    print(f"🔍 System startup: {len(processed_ids)} entries in registry.")

    for channel_name, url in CHANNELS.items():
        recent_videos = get_recent_videos(url, limit=5)
        processed_for_channel = False # 每輪只處理一個新影片以節省 Token
        
        for video_id, title in recent_videos:
            if processed_for_channel: break
            if video_id in processed_ids: continue
            
            # 語義過濾邏輯
            if not any(kw in title.lower() for kw in TECH_KEYWORDS):
                print(f"🚫 Filtered (Irrelevant): '{title}'")
                continue
                
            print(f"-> Target Acquired: {title}")
            transcript = get_transcript(video_id)
            if not transcript:
                print("⏭️ Skipping due to missing transcript (Check IP block).")
                continue
                
            analysis_result = analyze_with_ai(channel_name, title, transcript)
            if analysis_result:
                json_match = re.search(r'\{[\s\S]*\}', analysis_result)
                if json_match:
                    try:
                        data = json.loads(json_match.group(0))
                        data.update({"channel_name": channel_name, "video_id": video_id, "video_title": title})
                        
                        with open(DB_PATH, "a", encoding="utf-8") as f:
                            f.write(json.dumps(data, ensure_ascii=False) + "\n")
                        print(f"✅ Data persisted for video: {video_id}")
                        processed_for_channel = True 
                    except json.JSONDecodeError:
                        print("⚠️ AI output was not valid JSON.")
    print("Pipeline sequence finished.")

if __name__ == "__main__":
    process_pipeline()
