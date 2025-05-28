import subprocess
import os
import requests

# === Configuration ===
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"  # Use full tokenized URL if necessary
rtmp_url = os.getenv("RTMP_URL")  # Set your RTMP URL as an environment variable
background_img = "background.png"
logo_img = "logo.png"
ffmpeg_log = "ffmpeg_output.log"

# === Validate Environment Variable ===
if not rtmp_url:
    print("❌ Error: RTMP_URL environment variable is not set.")
    exit(1)

# === Check if Audio Stream is Reachable ===
def is_stream_online(url):
    try:
        response = requests.head(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://zeno.fm/"
        }, timeout=5)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ Error checking stream: {e}")
        return False

if not is_stream_online(audio_url):
    print(f"❌ Error: Audio stream {audio_url} is not reachable (HTTP 404 or offline).")
    exit(1)

# === FFmpeg Command ===
ffmpeg_cmd = [
    "ffmpeg",
    "-re",
    "-user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123.0.0.0 Safari/537.36",
    "-headers", "Referer: https://zeno.fm/\r\n",
    "-i", audio_url,
    "-loop", "1", "-i", background_img,
    "-i", logo_img,
    "-filter_complex",
    "[0:a]avectorscope=s=1280x720:r=30,format=rgba,hue=h='mod(360*t/15,360)'[viz];"
    "[viz]scale=w=1280:h=720:eval=frame[exp_viz];"
    "[1:v]scale=1280:720[bg];"
    "[2:v]scale=200:200[logo];"
    "[bg][exp_viz]overlay=x='(W-w)/2':y='(H-h)/2'[bgviz];"
    "[bgviz][logo]overlay="
    "x='abs(mod(200*t, (W-w)*2) - (W-w))':"
    "y='abs(mod(150*t, (H-h)*2) - (H-h))'[out]",
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast",
    "-tune", "zerolatency", "-b:v", "1000k",
    "-map", "0:a", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
    "-f", "flv", rtmp_url
]

# === Run FFmpeg with Logging ===
try:
    with open(ffmpeg_log, "w") as log_file:
        print("🚀 Starting FFmpeg stream...")
        process = subprocess.Popen(ffmpeg_cmd, stderr=log_file, stdout=log_file)
        process.wait()
        print("✅ FFmpeg process ended.")
except FileNotFoundError:
    print("❌ Error: FFmpeg not found. Ensure it is installed and in your PATH.")
except Exception as e:
    print(f"❌ Unexpected error occurred: {e}")
