import subprocess
import os

# Configuration
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = os.getenv("RTMP_URL")  # RTMP URL from GitHub Secrets
background_img = "background.png"
logo_img = "logo.png"

if not rtmp_url:
    print("Error: RTMP_URL environment variable is not set.")
    exit(1)

ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,
    "-loop", "1", "-i", background_img",  # Background
    "-i", logo_img,  # Logo
    "-filter_complex",
    # 1. High-Quality Circular Spectrum Visualizer
    "[0:a]showspectrum=size=720x720:mode=polar:color=rainbow:legend=0:scale=log,format=rgba[spectrum];"
    # 2. Scale background
    "[1:v]scale=1280:720[bg];"
    # 3. Overlay visualizer centered on background
    "[bg][spectrum]overlay=(W-w)/2:(H-h)/2[bgviz];"
    # 4. Make the logo bounce on every edge smoothly
    "[2:v]scale=200:200[logo];"
    "[bgviz][logo]overlay="
    "x='mod(300*t, W-200)':"
    "y='mod(200*t, H-200)'[out]",
    "-map", "[out]", "-map", "0:a",
    "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency",
    "-b:v", "2000k",
    "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", rtmp_url
]

# Run FFmpeg with logging
try:
    with open("ffmpeg_output.log", "w") as log_file:
        process = subprocess.Popen(ffmpeg_cmd, stderr=log_file, stdout=log_file)
        print("FFmpeg stream started.")
        process.wait()
except FileNotFoundError:
    print("Error: FFmpeg not found. Ensure it is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
