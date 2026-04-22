import os
import json
import re
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

# Define target channels for relational discourse mapping
CHANNELS = {
    "Matthew Berman": "https://www.youtube.com/@matthew_berman/videos", 
    "AI Explained": "https://www.youtube.com/@AIExplained/videos"
}

def load_processed_ids(filepath="discourse_data.jsonl"):
    """Loads previously processed video IDs to prevent redundant token consumption."""
    processed = set()
    if not os.path.exists(filepath):
        print(f"DEBUG: {filepath} not found.")
        return processed
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    vid = data.get("video_id")
                    if vid:
                        processed.add(vid)
                except json.JSONDecodeError as e:
                    print(f"DEBUG: Skip malformed line: {e}")
                    continue
    except Exception as e:
        print(f"DEBUG: Error reading file: {e}")
        
    print(f"DEBUG: Loaded IDs: {processed}")
    return processed

def get_recent_videos(channel_url, limit=5):
    """Fetches the latest N videos to cross-reference with the processed registry."""
    print(f"\n1. Fetching top {limit} recent videos from {channel_url}...")
    
    ydl_opts = {
        'extract_flat': True,
        'playlist_items': f'1-{limit}', # Fetch a small batch instead of just 1
        'quiet': True,
        'no_warnings': True
    }
    
    videos = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        videos.append((entry['id'], entry['title']))
    except Exception as e:
        print(f"⚠️ yt-dlp extraction error: {e}")
        
    return videos

def get_transcript(video_id):
    """Fetches the CC subtitles using the instantiated class method."""
    print(f"2. Extracting subtitles for video ID: {video_id}...")
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        return " ".join(t.text for t in transcript_list)
    except Exception as e:
        print(f"⚠️ Subtitle extraction failed: {e}")
        return None

def analyze_with_ai(channel_name, title, transcript):
    """使用 ChatAnywhere 接口進行自動化語意分析"""
    print(f"3. Handing data over to ChatAnywhere (gpt-5.4-mini)...")
    
    api_key = os.getenv("CHATANYWHERE_API_KEY") # 從 GitHub Secrets 讀取 
    if not api_key:
        print("⚠️ Error: CHATANYWHERE_API_KEY not found.")
        return None

    client = OpenAI(api_key=api_key, base_url="https://api.chatanywhere.org/v1")

    prompt = f"""
    Analyze this YouTube transcript as a Digital Ethnographer.
    Channel: {channel_name} | Title: {title}
    Output strictly in JSON. Hierarchy:
    {{
        "metadata": {{"sentiment": "Positive/Neutral/Negative", "technical_complexity": "Beginner/Advanced"}},
        "analysis": {{"speaker_stance": "...", "key_technologies": ["..."], "ideological_cluster": "...", "relational_mapping": {{"allies": [], "competitors": [], "critiques": ""}}}},
        "risk_assessment": {{"copyright_risk": "Low/Medium/High", "reasoning": "..."}}
    }}
    Transcript: {transcript[:25000]}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[{"role": "system", "content": "You are a professional AI risk analyst."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ API Call failed: {e}")
        return None

def process_pipeline():
    """Main execution pipeline with double-layer token protection."""
    db_path = "discourse_data.jsonl"
    processed_ids = load_processed_ids(db_path)
    print(f"🔍 System startup: Found {len(processed_ids)} previously processed videos in database.")

    for channel_name, url in CHANNELS.items():
        recent_videos = get_recent_videos(url, limit=5)
        
        # Guardrail: Process ONE new video per channel per run to strictly control Token burn rate
        processed_for_channel = False
        
        for video_id, title in recent_videos:
            if processed_for_channel:
                break
                
            # 第一層保護：檢查是否處理過 (Stateful check)
            if video_id in processed_ids:
                print(f"⏭️ Skipping '{title}' (Already in database).")
                continue
            
            # 第二層保護：關鍵字過濾（防止抓到不相關影片）
            # 只有標題包含這些關鍵字才進行分析
            tech_keywords = ["ai", "llm", "gpt", "model", "llama", "claude", "agent", "intelligence"]
            if not any(kw in title.lower() for kw in tech_keywords):
                print(f"🚫 Filtering out non-AI content: '{title}' (Token saved!)")
                continue
                
            print(f"-> Target locked on RELEVANT Video: {title}")
            transcript = get_transcript(video_id)
            
            if not transcript:
                print("⚠️ No transcript available. Skipping...")
                continue
                
            analysis_result = analyze_with_ai(channel_name, title, transcript)
            
            if analysis_result:
                json_match = re.search(r'\{[\s\S]*\}', analysis_result)
                if json_match:
                    try:
                        data = json.loads(json_match.group(0))
                        data["channel_name"] = channel_name
                        data["video_id"] = video_id
                        data["video_title"] = title
                        
                        with open(db_path, "a", encoding="utf-8") as f:
                            f.write(json.dumps(data, ensure_ascii=False) + "\n")
                        print("✅ Data verified and appended. Updated stateful registry.")
                        
                        processed_ids.add(video_id) # Update state in memory
                        processed_for_channel = True # Stop after 1 successful analysis per channel
                    except json.JSONDecodeError:
                        print("⚠️ JSON validation failed. Manual inspection required.")
                else:
                    print("⚠️ Could not locate JSON structure in the model's output.")

if __name__ == "__main__":
    process_pipeline()