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
    # **Super Low Latency Settings**
    "-fflags", "nobuffer", "-flags", "low_delay",  # Remove buffering
    "-strict", "experimental",  # Allow real-time optimizations
    "-probesize", "16", "-analyzeduration", "0",  # Minimize delay in analyzing input
    "-filter_complex",
    # Spiral visualizer with smooth color transitions
    "[0:a]avectorscope=s=1280x720:r=30:rc=1:gc=1:bc=1:zoom=1.5,rotate=PI*t/5,format=rgba[viz];"
    "[viz]hue='H=2*t*50':s=2.5:b=1.5[vizcolor];"  # Dynamic color shift
    # Background and scaling
    "[1:v]scale=1280:720[bg];"
    # Rotating logo effect (like a CD)
    "[2:v]scale=500:500,rotate=2*PI*t/3:c=none[logo];"
    # Overlay effects
    "[bg][vizcolor]overlay=W/2-w/2:H/2-h/2[bgviz];"
    "[bgviz][logo]overlay=W/2-w/2:50[out]",
    # **Real-time Encoding Settings**
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-b:v", "1000k",
    "-g", "25", "-r", "30",  # Low keyframe interval, real-time FPS
    "-map", "0:a", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-af", "aresample=async=1",
    "-bufsize", "500k",  # Reduce buffer size for smooth real-time streaming
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
