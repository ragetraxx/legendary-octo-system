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

ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,
    "-loop", "1", "-i", background_img,  # Background input
    "-i", logo_img,                       # Logo input
    "-filter_complex",
    "[0:a]avectorscope=s=1920x1080:r=30,format=rgba,hue=h='mod(360*t/10,360)'[viz];"
    "[viz]scale=w=1920*(0.2+0.8*abs(sin(2*PI*t/10))):h=1080*(0.2+0.8*abs(sin(2*PI*t/10))):eval=frame[exp_viz];"
     # Scale background and logo
    "[1:v]scale=1280:720[bg];"
    "[2:v]scale=200:200[logo];"
    # Overlay the expanded visualizer centered on the background
    "[bg][exp_viz]overlay=x=0:y=0[bgviz];"
    # Overlay the bouncing logo that reflects off every edge
    "[bgviz][logo]overlay="
    "x='abs(mod(200*t, (W-w)*2) - (W-w))':"
    "y='abs(mod(150*t, (H-h)*2) - (H-h))'[out]",
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast",
    "-tune", "zerolatency", "-b:v", "1000k",
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
