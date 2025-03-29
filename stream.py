import subprocess
import os

# Configuration
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = os.getenv("RTMP_URL")  # Get RTMP URL from environment variable
background_img = "background.png"
logo_img = "logo.png"

if not rtmp_url:
    print("Error: RTMP_URL environment variable is not set.")
    exit(1)

# FFmpeg command with realistic bouncing logo and circular color-changing visualizer
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,
    "-loop", "1", "-i", background_img,  # Background
    "-i", logo_img,  # Logo
    "-filter_complex",
    # Circular visualizer with color change every 15s
    "[0:a]avectorscope=s=720x720:r=30,"
    "geq=r='sin(PI*t/15)*255':g='cos(PI*t/15)*255':b='sin(2*PI*t/15)*255',"
    "format=rgba[viz];"
    # Scale background and logo
    "[1:v]scale=1280:720[bg];"
    "[2:v]scale=200:200[logo];"
    # Combine background and visualizer
    "[bg][viz]overlay=(W-w)/2:(H-h)/2[bgviz];"
    # Bouncing logo effect with real reflections
    "[bgviz][logo]overlay="
    "x='W/2 + (W/2-200) * sin(2*PI*t/3)':"
    "y='H/2 + (H/2-200) * cos(2*PI*t/4)'[out]",
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-b:v", "1000k",
    "-map", "0:a", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
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
