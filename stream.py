import os
import subprocess

# Configuration
stream_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = os.getenv("RTMP_URL")
background_img = "background.png"
logo_img = "logo.png"
ffmpeg_log = "ffmpeg_output.log"

if not rtmp_url:
    print("❌ Error: RTMP_URL environment variable is not set.")
    exit(1)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://zeno.fm/"
}

# FFmpeg command optimized for low bandwidth (~300–500 kbps total)
ffmpeg_cmd = [
    "ffmpeg",
    "-re",
    "-user_agent", HEADERS["User-Agent"],
    "-headers", f"Referer: {HEADERS['Referer']}\r\n",
    "-i", stream_url,
    "-loop", "1", "-i", background_img,
    "-i", logo_img,
    "-filter_complex",
    "[0:a]avectorscope=s=640x360:r=15,format=rgba,hue=h='mod(360*t/15,360)'[viz];"
    "[viz]scale=w=640:h=360:eval=frame[exp_viz];"
    "[1:v]scale=640:360[bg];"
    "[2:v]scale=100:100[logo];"
    "[bg][exp_viz]overlay=x='(W-w)/2':y='(H-h)/2'[bgviz];"
    "[bgviz][logo]overlay="
    "x='abs(mod(100*t, (W-w)*2) - (W-w))':"
    "y='abs(mod(75*t, (H-h)*2) - (H-h))'[out]",
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast",
    "-tune", "zerolatency", "-b:v", "200k",
    "-map", "0:a", "-c:a", "aac", "-b:a", "96k", "-ac", "1", "-ar", "44100",
    "-f", "flv", rtmp_url
]

try:
    with open(ffmpeg_log, "w") as log_file:
        print("🚀 Starting FFmpeg stream (low bandwidth)...")
        process = subprocess.Popen(ffmpeg_cmd, stderr=log_file, stdout=log_file)
        process.wait()
        print("✅ FFmpeg process completed.")
except FileNotFoundError:
    print("❌ FFmpeg not found. Install it and make sure it's in your PATH.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
