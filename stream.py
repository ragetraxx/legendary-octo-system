import subprocess
import os

# Configuration
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = os.getenv("RTMP_URL")  # Get RTMP URL from environment variable
logo_img = "logo.png"

if not rtmp_url:
    print("Error: RTMP_URL environment variable is not set.")
    exit(1)

ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,
    "-i", logo_img,  # Logo input
    "-filter_complex",
    # Create full-screen visualizer at 1280x720 with hue cycling
    "[0:a]avectorscope=s=1280x720:r=30,format=rgba,hue=h='mod(360*t/15,360)'[viz];"
    # Expand/contract dynamically
    "[viz]scale=w=1280*(1+0.3*sin(2*PI*t/10)):h=720*(1+0.3*sin(2*PI*t/10)):eval=frame[exp_viz];"
    # Overlay the bouncing logo
    "[exp_viz][1:v]overlay="
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
        process = subprocess.Popen(" ".join(ffmpeg_cmd), stderr=log_file, stdout=log_file, shell=True)
        print("FFmpeg stream started.")
        process.wait()
except FileNotFoundError:
    print("Error: FFmpeg not found. Ensure it is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
