import os
import sys
import json
import ssl
from pathlib import Path

# Bypass macOS SSL certificate verification error 
ssl._create_default_https_context = ssl._create_unverified_context

try:
    import whisper
except ImportError:
    print("Please install whisper: pip install openai-whisper")
    sys.exit(1)

def get_project_root():
    return Path(__file__).resolve().parents[1]

def main():
    root = get_project_root()
    data_dir = root / "data"
    out_dir = root / "assets" / "subtitles"
    
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if there are videos in data/
    if not data_dir.exists():
        print(f"Data directory not found at {data_dir}")
        sys.exit(1)
        
    videos = list(data_dir.glob("*.mp4"))
    if not videos:
        print(f"No .mp4 files found in {data_dir}")
        return
        
    print("Loading whisper model ('base')...")
    model = whisper.load_model("base")
    
    for video_path in videos:
        vid_name = video_path.stem
        out_json_path = out_dir / f"{vid_name}_subs.json"
        
        if out_json_path.exists():
            print(f"Skipping {vid_name}, subtitle already exists: {out_json_path}")
            continue
            
        print(f"Transcribing {vid_name}.mp4 ...")
        result = model.transcribe(str(video_path))
        
        subs = []
        for segment in result.get("segments", []):
            subs.append({
                "start_sec": segment["start"],
                "end_sec": segment["end"],
                "text": segment["text"].strip()
            })
            
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(subs, f, indent=2, ensure_ascii=False)
            
        print(f"[{vid_name}] Done. Saved to {out_json_path}")

if __name__ == "__main__":
    main()
