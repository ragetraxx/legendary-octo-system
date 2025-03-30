import subprocess
import os
import requests
import re
import time
import threading

# Configuration
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = os.getenv("RTMP_URL")  # Get RTMP URL from environment variable
background_img = "background.png"
logo_img = "logo.png"
metadata_file = "metadata.txt"  # Temp file to update metadata

if not rtmp_url:
    print("Error: RTMP_URL environment variable is not set.")
    exit(1)

def get_metadata():
    """Fetches metadata from the audio stream."""
    try:
        headers = {"Icy-MetaData": "1"}
        response = requests.get(audio_url, headers=headers, stream=True, timeout=5)
        
        if "icy-metaint" in response.headers:
            metaint = int(response.headers["icy-metaint"])
            stream = response.raw
            stream.read(metaint)  # Skip to metadata
            metadata_length = ord(stream.read(1)) * 16
            
            if metadata_length > 0:
                metadata = stream.read(metadata_length).decode("utf-8", errors="ignore")
                match = re.search(r"StreamTitle='(.*?)';", metadata)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"Error fetching metadata: {e}")
    return "Unknown Track"

def update_metadata():
    """Continuously updates metadata text file in real time."""
    last_track = ""
    while True:
        track_info = get_metadata()
        if track_info != last_track:  # Only update if changed
            with open(metadata_file, "w") as f:
                f.write(track_info)
            last_track = track_info
        time.sleep(3)  # Update every 3 seconds for real-time display

# Start metadata updating in a separate thread
threading.Thread(target=update_metadata, daemon=True).start()

# FFmpeg command with real-time metadata overlay
ffmpeg_cmd = [
    "ffmpeg", "-re", "-i", audio_url,
    "-loop", "1", "-i", background_img,
    "-i", logo_img,
    "-vf",
    "[1:v]scale=1280:720[bg];"
    "[2:v]scale=200:200[logo];"
    "[bg][logo]overlay=W-w-20:H-h-20[bg_logo];"
    f"[bg_logo]drawtext=textfile={metadata_file}:fontcolor=white:fontsize=40:x=20:y=H-h-50:reload=1[out]",
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-b:v", "1000k",
    "-map", "0:a", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", rtmp_url
]

# Run FFmpeg with logging and real-time processing
try:
    with open("ffmpeg_output.log", "w") as log_file:
        process = subprocess.Popen(ffmpeg_cmd, stderr=log_file, stdout=log_file, bufsize=0)
        print("FFmpeg stream started.")
        process.wait()
except FileNotFoundError:
    print("Error: FFmpeg not found. Ensure it is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
