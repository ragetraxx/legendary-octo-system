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
    "-i", logo_img,  # Logo input
    "-filter_complex",
    # Create a **circular** visualizer with a ripple expansion effect
    "[0:a]showspectrum=size=720x720:mode=polar:color=rainbow:legend=0:scale=log,format=rgba,"
    "geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)'[viz];"
    # Dynamically scale the visualizer (pulsing effect)
    "[viz]scale=w=720*(1+0.3*sin(2*PI*t/10)):h=720*(1+0.3*sin(2*PI*t/10)):eval=frame[exp_viz];"
    # Scale background and logo
    "[1:v]scale=1280:720[bg];"
    "[2:v]scale=200:200[logo];"
    # Overlay the **dynamic visualizer** at the center
    "[bg][exp_viz]overlay=x='(W-w)/2':y='(H-h)/2'[bgviz];"
    # Ensure the **logo bounces smoothly**
    "[bgviz][logo]overlay="
    "x='abs(mod(300*t, (W-w)*2) - (W-w))':"
    "y='abs(mod(250*t, (H-h)*2) - (H-h))'[out]",
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast",
    "-tune", "zerolatency", "-b:v", "2000k",
    "-map", "0:a", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", rtmp_url
]

# Run FFmpeg with logging
try:
    with open("ffmpeg_output.log", "w") as log_file:
        print("Starting FFmpeg stream...")
        process = subprocess.Popen(ffmpeg_cmd, stderr=log_file, stdout=log_file)
        print("FFmpeg process started.")
        process.wait()
except FileNotFoundError:
    print("Error: FFmpeg not found. Ensure it is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
