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

# FFmpeg command with optimizations for lower buffer
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,  # Read audio in real-time
    "-loop", "1", "-i", background_img,  # Background
    "-i", logo_img,  # Logo
    "-probesize", "32", "-analyzeduration", "0", "-fflags", "nobuffer",  # Lower latency
    "-filter_complex",
    # Spiral visualizer with smooth color transitions
    "[0:a]avectorscope=s=1280x720:r=30:rc=1:gc=1:bc=1:zoom=1.5,rotate=PI*t/5,format=rgba[viz];"
    "[viz]eq=saturation=2.5,curves=r='0/1 0.5/0.5 1/0':g='0/0 0.5/1 1/0':b='0/0 0.5/0 1/1'[vizcolor];"
    # Background and scaling
    "[1:v]scale=1280:720[bg];"
    # Rotating logo effect (like a CD)
    "[2:v]scale=500:500,rotate=2*PI*t/5:c=none[logo];"
    # Overlay effects
    "[bg][vizcolor]overlay=W/2-w/2:H/2-h/2[bgviz];"
    "[bgviz][logo]overlay=W/2-w/2:50[out]",
    # Video encoding optimizations
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-b:v", "1000k",
    "-g", "25",  # Low keyframe interval to reduce delay
    "-map", "0:a", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-af", "asetpts=PTS-STARTPTS",
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
