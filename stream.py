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

# FFmpeg command with real-time optimizations
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,  # Read audio in real-time
    "-loop", "1", "-i", background_img,  # Background
    "-i", logo_img,  # Logo
    "-fflags", "nobuffer", "-flags", "low_delay",  # Remove buffering
    "-strict", "experimental",
    "-probesize", "16", "-analyzeduration", "0",  # Minimize delay
    "-filter_complex",
    # Fixed: Corrected syntax and added commas
    "[0:a]avectorscope=s=1280x720:r=30:rc=1:gc=1:bc=1:zoom=1.5,rotate=PI*t/5,format=rgba[viz];"
    "[viz]hue=H=2*t*50:s=2.5:b=1.5[vizcolor];"  # Dynamic color shift
    "[1:v]scale=1280:720[bg];"
    "[2:v]scale=500:500,rotate=2*PI*t/3:c=none[logo];"
    "[bg][vizcolor]overlay=W/2-w/2:H/2-h/2[bgviz];"
    "[bgviz][logo]overlay=W/2-w/2:50[out]",
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-b:v", "1000k",
    "-g", "25", "-r", "30",
    "-map", "0:a", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-bufsize", "500k",
    "-f", "flv", rtmp_url
]

# Run FFmpeg and capture output
log_file_path = "ffmpeg_output.log"
try:
    with open(log_file_path, "w") as log_file:
        process = subprocess.Popen(ffmpeg_cmd, stderr=log_file, stdout=log_file)
        print(f"FFmpeg stream started. Check logs: {log_file_path}")
        process.wait()
except FileNotFoundError:
    print("Error: FFmpeg not found. Ensure it is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
