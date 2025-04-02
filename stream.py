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

# Define the FFmpeg command as a list
ffmpeg_cmd = [
    "ffmpeg", "-re", "-i", audio_url,
    "-loop", "1", "-i", background_img,
    "-i", logo_img,
    "-filter_complex",
    "[0:a]avectorscope=s=1280x720:r=30,format=rgba,hue=h='mod(360*t/10,360)'[viz1];"
    "[0:a]showcqt=s=1280x720:r=30:fps=30:bar_g=10[out1];"
    "[viz1][out1]blend=all_mode='addition'[viz];"
    "[viz]scale=w=1280*(1+0.3*sin(2*PI*t/10)):h=720*(1+0.3*sin(2*PI*t/10)):eval=frame[exp_viz];"
    "[1:v]scale=1280:720,boxblur=5:5[bg];"
    "[2:v]scale=200:200,rotate=0.2*sin(2*PI*t/5)[logo];"
    "[bg][exp_viz]overlay=x='(W-w)/2':y='(H-h)/2'[bgviz];"
    "[bgviz][logo]overlay="
    "x='(W-200)/2+100*sin(2*PI*t/5)':"
    "y='(H-200)/2+100*cos(2*PI*t/5)'[out]",
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
