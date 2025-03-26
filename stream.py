import subprocess
import os
import time

# Configuration
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = os.getenv("RTMP_URL")  # Get RTMP URL from environment variable
background_img = "background.png"
logo_img = "logo.png"

if not rtmp_url:
    print("Error: RTMP_URL environment variable is not set.")
    exit(1)

def start_ffmpeg():
    ffmpeg_cmd = [
        "ffmpeg",
        "-re", "-i", audio_url,
        "-loop", "1", "-i", background_img,  # Background
        "-i", logo_img,  # Logo
        "-fflags", "nobuffer", "-flags", "low_delay",
        "-strict", "experimental",
        "-probesize", "16", "-analyzeduration", "0",
        "-filter_complex",
        "[0:a]showspectrum=size=1280x720:mode=separate:color=intensity:scale=log:legend=0,format=rgba[viz];"
        "[1:v]scale=1280:720[bg];"
        "[2:v]scale=500:500,rotate=2*PI*t/60:c=none[logo];"
        "[bg][viz]overlay=(W-w)/2:(H-h)/2[bgviz];"
        "[bgviz][logo]overlay=(W-w)/2:50[out]",
        "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-b:v", "1000k",
        "-g", "25", "-r", "30",
        "-map", "0:a", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
        "-f", "flv", rtmp_url
    ]

    log_file_path = "ffmpeg_output.log"

    while True:
        try:
            with open(log_file_path, "w") as log_file:
                process = subprocess.Popen(ffmpeg_cmd, stderr=log_file, stdout=log_file)
                print("FFmpeg stream started.")
                process.wait()

                # If FFmpeg crashes, print error log
                print("\n🔴 FFmpeg crashed! Showing last 10 lines of log:")
                with open(log_file_path, "r") as log_file:
                    lines = log_file.readlines()
                    print("".join(lines[-10:]))  # Print last 10 lines of log

                print("⏳ Restarting FFmpeg in 5 seconds...")
                time.sleep(5)  # Wait before restart

        except FileNotFoundError:
            print("Error: FFmpeg not found. Ensure it is installed and in your PATH.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

# Start FFmpeg streaming
start_ffmpeg()
