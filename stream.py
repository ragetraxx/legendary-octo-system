import subprocess
import os

# Configuration
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = os.getenv("RTMP_URL")  # RTMP URL from environment variable
background_img = "background.png"
logo_img = "logo.png"

if not rtmp_url:
    print("Error: RTMP_URL environment variable is not set.")
    exit(1)

ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,
    "-loop", "1", "-i", background_img,  # Background
    "-i", logo_img,  # Logo
    "-filter_complex",
    # 1. Circular spectrum with smooth color transitions
    "[0:a]showspectrum=size=720x720:mode=polar:color=rainbow:legend=0:scale=log,format=rgba[spectrum];"
    # 2. Expanding & contracting effect (pulsation effect)
    "[spectrum]scale=w=720*(1+0.2*sin(2*PI*t/2)):h=720*(1+0.2*sin(2*PI*t/2)):eval=frame[pulsating_spectrum];"
    # 3. Scale background and logo
    "[1:v]scale=1280:720[bg];"
    "[2:v]scale=200:200[logo];"
    # 4. Overlay the visualizer centered on the background
    "[bg][pulsating_spectrum]overlay=(W-w)/2:(H-h)/2[bgviz];"
    # 5. Make the logo bounce smoothly
    "[bgviz][logo]overlay="
    "x='W/2 + (W/3) * sin(2*PI*t/3)':"
    "y='H/2 + (H/3) * cos(2*PI*t/3)'[out]",
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
