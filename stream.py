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

# FFmpeg command:
# - The audio is visualized using avectorscope (a circular visualizer),
#   piped through the hue filter to cycle colors every 15 seconds.
# - The background is scaled to 1280x720.
# - The logo is scaled to 200x200.
# - The visualizer is overlaid centered on the background.
# - Finally, the logo is overlaid with a bouncing effect using mod() and abs()
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,
    "-loop", "1", "-i", background_img,  # Background input
    "-i", logo_img,  # Logo input
    "-filter_complex",
    # Create circular visualizer and change hue over time
    "[0:a]avectorscope=s=720x720:r=30,format=rgba,hue=h='mod(360*t/15,360)'[viz];"
    # Scale background and logo
    "[1:v]scale=1280:720[bg];"
    "[2:v]scale=200:200[logo];"
    # Overlay visualizer on the center of the background
    "[bg][viz]overlay=(W-w)/2:(H-h)/2[bgviz];"
    # Overlay bouncing logo on top; logo bounces off all screen edges
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
