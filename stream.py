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
    # 1. Circular spectrum visualizer with color cycling every 15 seconds
    "[0:a]showspectrum=s=720x720:mode=polar:color=rainbow:r=30,format=rgba,"
    "hue=h='mod(360*t/15,360)'[spectrum];"
    # 2. Expanding & contracting effect (pulsating effect)
    "[spectrum]scale=w=720*(1+0.3*sin(2*PI*t/2)):h=720*(1+0.3*sin(2*PI*t/2)):eval=frame[pulsating_spectrum];"
    # 3. Radial waves reacting to the music
    "[0:a]avectorscope=s=720x720:r=30:draw=line:scale=sqrt,format=rgba,"
    "hue=h='mod(360*t/10,360)'[waves];"
    # 4. Combine spectrum and waves
    "[pulsating_spectrum][waves]blend=all_mode=lighten[visualizer];"
    # 5. Scale background and logo
    "[1:v]scale=1280:720[bg];"
    "[2:v]scale=200:200[logo];"
    # 6. Overlay the visualizer at the center of the background
    "[bg][visualizer]overlay=x='(W-w)/2':y='(H-h)/2'[bgviz];"
    # 7. Make the logo bounce off the edges dynamically
    "[bgviz][logo]overlay="
    "x='abs(mod(300*t, (W-w)*2) - (W-w))':"
    "y='abs(mod(200*t, (H-h)*2) - (H-h))'[out]",
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
