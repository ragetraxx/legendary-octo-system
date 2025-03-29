import subprocess
import os

# Configuration
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = os.getenv("RTMP_URL")  # RTMP URL must be set in your environment
background_img = "background.png"
logo_img = "logo.png"

if not rtmp_url:
    print("Error: RTMP_URL environment variable is not set.")
    exit(1)

# FFmpeg command breakdown:
# 1. Create a spectrum visualizer (300x300) with rainbow colors.
# 2. Scale logo.png to 300x300 so it can serve as a design “mask.”
# 3. Blend the logo and the spectrum using the 'multiply' mode.
# 4. Scale the background to 1280x720.
# 5. Overlay the blended visualizer in the center of the background.
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,
    "-loop", "1", "-i", background_img,
    "-i", logo_img,
    "-filter_complex",
    # Generate a 300x300 spectrum from the audio.
    "[0:a]showspectrum=s=300x300:mode=bar:color=rainbow,format=rgba[spectrum];"
    # Scale the logo to 300x300.
    "[2:v]scale=300:300,format=rgba[logo];"
    # Blend the logo and the spectrum. The logo acts as a “mask” so that the spectrum shows through.
    "[logo][spectrum]blend=all_mode='multiply'[vis];"
    # Scale the background.
    "[1:v]scale=1280:720[bg];"
    # Overlay the blended visualizer onto the center of the background.
    "[bg][vis]overlay=x=(W-w)/2:y=(H-h)/2[output]",
    "-map", "[output]",
    "-map", "0:a",
    "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency",
    "-b:v", "1500k",
    "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", rtmp_url
]

try:
    with open("ffmpeg_output.log", "w") as log_file:
        process = subprocess.Popen(ffmpeg_cmd, stderr=log_file, stdout=log_file)
        print("FFmpeg stream started.")
        process.wait()
except FileNotFoundError:
    print("Error: FFmpeg not found. Ensure it is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
