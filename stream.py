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
    # Sine wave visualizer with color cycling
    "[0:a]sinewave=s=1920x1080:r=30:freq=1:amplitude=0.5,format=rgba,hue=h='mod(360*t/4,360)'[wave];"
    # Rotate and scale the sine wave visualizer
    "[wave]rotate='PI*t/4':w=1920:h=1080,scale=w=1920*(0.5+0.5*sin(2*PI*t/6)):h=1080*(0.5+0.5*sin(2*PI*t/6)):eval=frame[rot_wave];"
    # Overlay the visualizer onto the background
    "[1:v][rot_wave]overlay=x=0:y=0:format=auto[bgviz];"
    # Scale background and logo
    "[bgviz][2:v]scale=200:200[logo];"
    # Overlay the bouncing logo
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
