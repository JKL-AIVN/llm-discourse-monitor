import os
import json
import re
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

# 1. 確保頻道清單正確 (包含底線與 videos 字尾)
CHANNELS = {
    "Matthew Berman": "https://www.youtube.com/@matthew_berman/videos", 
    "AI Explained": "https://www.youtube.com/@AIExplained/videos"
}

# 2. 修改路徑邏輯：確保無論從哪裡執行，都能找到同目錄下的資料檔案
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "discourse_data.jsonl")

def load_processed_ids(filepath=DB_PATH):
    processed = set()
    if not os.path.exists(filepath):
        print(f"DEBUG: {filepath} not found.")
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
                except json.JSONDecodeError: continue
    except Exception as e:
        print(f"DEBUG: Error reading file: {e}")
    return processed

def get_recent_videos(channel_url, limit=5):
    print(f"\n1. Fetching recent videos from {channel_url}...")
    ydl_opts = {'extract_flat': True, 'playlist_items': f'1-{limit}', 'quiet': True, 'no_warnings': True}
    videos = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry: videos.append((entry['id'], entry['title']))
    except Exception as e:
        print(f"⚠️ yt-dlp error: {e}")
    return videos

def get_transcript(video_id):
    print(f"2. Extracting subtitles for: {video_id}...")
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        return " ".join(t.text for t in transcript_list)
    except Exception as e:
        print(f"⚠️ Subtitle failed: {e}")
        return None

def analyze_with_ai(channel_name, title, transcript):
    """核心分析邏輯：使用 OpenAI SDK 與 ChatAnywhere 接口"""
    print(f"3. Handing data over to ChatAnywhere (gpt-5.4-mini)...")
    api_key = os.getenv("CHATANYWHERE_API_KEY")
    if not api_key:
        print("❌ Error: CHATANYWHERE_API_KEY not found.")
        return None

    client = OpenAI(api_key=api_key, base_url="https://api.chatanywhere.org/v1")
    
    # 這裡填入你設計的結構化 Prompt
    prompt = f"""
    Analyze this YouTube transcript as a Digital Ethnographer.
    Channel: {channel_name} | Title: {title}
    Output strictly in JSON. Hierarchy:
    {{
        "metadata": {{"sentiment": "Positive/Neutral/Negative", "technical_complexity": "Beginner/Advanced"}},
        "analysis": {{
            "speaker_stance": "...", 
            "key_technologies": ["..."], 
            "ideological_cluster": "...", 
            "relational_mapping": {{"allies": [], "competitors": [], "critiques": ""}}
        }},
        "risk_assessment": {{"copyright_risk": "Low/Medium/High", "reasoning": "..."}}
    }}
    Transcript (Snippet): {transcript[:25000]}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[{"role": "system", "content": "You are a professional AI risk analyst."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return None

def process_pipeline():
    processed_ids = load_processed_ids(DB_PATH)
    print(f"🔍 System startup: Found {len(processed_ids)} processed videos.")

    for channel_name, url in CHANNELS.items():
        recent_videos = get_recent_videos(url, limit=5)
        processed_for_channel = False
        
        for video_id, title in recent_videos:
            if processed_for_channel: break
            if video_id in processed_ids: continue
            
            # 關鍵字過濾
            tech_keywords = ["ai", "llm", "gpt", "model", "llama", "claude", "agent", "intelligence"]
            if not any(kw in title.lower() for kw in tech_keywords):
                print(f"🚫 Filtering non-AI content: '{title}'")
                continue
                
            print(f"-> Target locked: {title}")
            transcript = get_transcript(video_id)
            if not transcript: continue
                
            analysis_result = analyze_with_ai(channel_name, title, transcript)
            if analysis_result:
                json_match = re.search(r'\{[\s\S]*\}', analysis_result)
                if json_match:
                    try:
                        data = json.loads(json_match.group(0))
                        data.update({"channel_name": channel_name, "video_id": video_id, "video_title": title})
                        with open(DB_PATH, "a", encoding="utf-8") as f:
                            f.write(json.dumps(data, ensure_ascii=False) + "\n")
                        print("✅ Data verified and appended.")
                        processed_for_channel = True 
                    except json.JSONDecodeError: print("⚠️ JSON validation failed.")
    print("Done.")

if __name__ == "__main__":
    process_pipeline()
