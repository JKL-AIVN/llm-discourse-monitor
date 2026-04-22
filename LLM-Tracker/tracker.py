import os
import json
import re
import yt_dlp
import subprocess
import tempfile
from youtube_transcript_api import YouTubeTranscriptApi

# Define target channels for relational discourse mapping
CHANNELS = {
    "Matthew Berman": "https://www.youtube.com/@matthew_berman/videos", 
    "AI Explained": "https://www.youtube.com/@AIExplained/videos"
}

def load_processed_ids(filepath="discourse_data.jsonl"):
    """Loads previously processed video IDs."""
    processed = set()
    if not os.path.exists(filepath):
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
                except:
                    continue
    except Exception as e:
        print(f"⚠️ Error reading database: {e}")
        
    return processed

def get_recent_videos(channel_url, limit=10):
    """Fetches the latest N videos."""
    print(f"\n1. Fetching top {limit} recent videos from {channel_url}...")
    
    ydl_opts = {
        'extract_flat': True,
        'playlist_items': f'1-{limit}',
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
        print(f"⚠️ yt-dlp error: {e}")
        
    return videos

def get_transcript(video_id):
    """Fetches video transcript."""
    print(f"2. Extracting subtitles for: {video_id}...")
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        return " ".join(t.text for t in transcript_list)
    except Exception as e:
        print(f"⚠️ Subtitle extraction failed: {e}")
        return None

def analyze_with_gemini(channel_name, title, transcript):
    """Calls local Gemini CLI securely using a permitted project-specific temp directory."""
    print("3. Handing data over to Gemini CLI for semantic & IP risk analysis...")
    
    project_temp_dir = r"C:\Users\jackt\.gemini\tmp\llm-tracker"
    if not os.path.exists(project_temp_dir):
        os.makedirs(project_temp_dir, exist_ok=True)
    
    prompt = f"""
    Analyze this YouTube transcript as a Digital Ethnographer.
    Channel: {channel_name}
    Video Title: {title}
    
    Output strictly in JSON. Ensure the structure follows this specific hierarchy:
    {{
        "metadata": {{
            "sentiment": "Positive/Neutral/Negative",
            "technical_complexity": "Beginner/Advanced"
        }},
        "analysis": {{
            "speaker_stance": "Short description",
            "key_technologies": ["List", "of", "entities"], 
            "ideological_cluster": "e.g., Accelerationism, Safety First, Open Source",
            "relational_mapping": {{
                "allies": ["Channel/Entity names"],
                "competitors": ["Channel/Entity names"],
                "critiques": "Who or what is the speaker refuting?"
            }}
        }},
        "risk_assessment": {{
            "copyright_risk": "Low/Medium/High",
            "reasoning": "Brief legal/ethical explanation"
        }}
    }}
    """

    with tempfile.NamedTemporaryFile(
        mode='w+', 
        delete=False, 
        encoding='utf-8', 
        dir=project_temp_dir, 
        suffix=".txt"
    ) as temp_file:
        temp_file.write(prompt + "\n\n--- Transcript Start ---\n\n" + transcript)
        temp_path = temp_file.name

    try:
        cli_command = "gemini.cmd" if os.name == 'nt' else "gemini"
        result = subprocess.run(
            [cli_command, "ask", f"Read the file at {temp_path} and output strictly requested JSON."],
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=(os.name == 'nt')
        )
        
        if result.returncode != 0:
            print(f"⚠️ Gemini CLI error: {result.stderr}")
            return None
            
        return result.stdout.strip()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def compare_channels():
    """Generates a comparison report."""
    print("\n--- Comparative Analysis Phase ---")
    db_path = "discourse_data.jsonl"
    if not os.path.exists(db_path):
        print("No data to compare.")
        return

    data_points = []
    with open(db_path, "r", encoding="utf-8") as f:
        for line in f:
            data_points.append(line.strip())

    if not data_points:
        print("No data points found.")
        return

    # Compare last 15 videos
    summary_data = "\n".join(data_points[-15:])
    
    prompt = f"""
    Compare the discourse styles of 'Matthew Berman' and 'AI Explained' based on these analysis records:
    {summary_data}
    
    Who is more technical? Who is more hype-focused? What are their distinct viewpoints?
    """

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tf:
        tf.write(prompt)
        temp_path = tf.name

    try:
        print("Requesting comparison report...")
        # To avoid command line length limits, we'll use a slightly smaller summary if needed
        # but 15 JSON lines is usually okay (~10KB). Windows limit is 8KB though.
        # Let's use stdin redirection for the comparison as well.
        result = subprocess.run(
            f'type "{temp_path}" | gemini',
            capture_output=True,
            text=True,
            encoding='utf-8',
            shell=True
        )
        os.unlink(temp_path)
        
        # Clean up the report - sometimes Gemini CLI adds conversational filler
        report_content = result.stdout
        if "I will" in report_content and "generate" in report_content:
            # If it looks like it's just describing what it will do, we might need a better prompt
            pass

        print("\n=== REPORT ===\n")
        print(report_content)
        with open("comparison_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        print("\nReport saved to comparison_report.md")
    except Exception as e:
        print(f"⚠️ Comparison failed: {e}")
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def export_to_web_json(jsonl_path="discourse_data.jsonl", web_json_path="data.json"):
    """Converts raw JSONL logs into a structured JSON array for the frontend."""
    data_list = []
    if os.path.exists(jsonl_path):
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data_list.append(json.loads(line))
                except:
                    continue
        
        with open(web_json_path, "w", encoding="utf-8") as f:
            json.dump(data_list, f, ensure_ascii=False, indent=4)
        print(f"📊 Web-ready JSON exported to {web_json_path}")

def process_pipeline():
    """Main execution pipeline with double-layer token protection."""
    db_path = "discourse_data.jsonl"
    processed_ids = load_processed_ids(db_path)
    print(f"🔍 System startup: Found {len(processed_ids)} previously processed videos in database.")

    for channel_name, url in CHANNELS.items():
        recent_videos = get_recent_videos(url, limit=5)
        processed_for_channel = False
        
        for video_id, title in recent_videos:
            if processed_for_channel: 
                break
            
            # 第一層保護：檢查是否處理過
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
                
            analysis_result = analyze_with_gemini(channel_name, title, transcript)
            
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
                        
                        processed_ids.add(video_id)
                        processed_for_channel = True
                    except json.JSONDecodeError:
                        print("⚠️ JSON validation failed. Manual inspection required.")
                else:
                    print("⚠️ Could not locate JSON structure in the model's output.")

    compare_channels()
    export_to_web_json()

if __name__ == "__main__":
    process_pipeline()
