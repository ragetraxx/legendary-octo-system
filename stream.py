import os
import subprocess
import threading
import time
import sys

# === Configuration ===
stream_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = os.getenv("RTMP_URL")
background_img = "background.png"  # Ensure this is 720x1280
logo_img = "logo.png"
ffmpeg_log = "ffmpeg_output.log"

if not rtmp_url:
    print("❌ Error: RTMP_URL environment variable is not set.")
    sys.exit(1)

# === FFmpeg Command (Optimized for 9:16 Vertical) ===
ffmpeg_cmd = [
    "ffmpeg",
    "-re",
    "-i", stream_url,
    "-loop", "1", "-i", background_img,
    "-i", logo_img,
    "-filter_complex",
    # 1. Create the audio visualizer at vertical scale
    "[0:a]avectorscope=s=720x1280:r=25,format=rgba,hue=h='mod(360*t/15,360)'[viz];"
    # 2. Scale background to exactly 720x1280
    "[1:v]scale=720:1280[bg];"
    # 3. Scale logo
    "[2:v]scale=200:-1[logo];"
    # 4. Overlay visualizer onto background
    "[bg][viz]overlay=(W-w)/2:(H-h)/2[bgviz];"
    # 5. Floating logo animation
    "[bgviz][logo]overlay="
    "x='abs(mod(100*t\\,(W-w)*2)-(W-w))':"
    "y='abs(mod(75*t\\,(H-h)*2)-(H-h))'[out]",
    "-map", "[out]",
    "-c:v", "libx264",        # libx264 is more stable for GH Actions than x265
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-b:v", "2500k",          # Increased bitrate for 720p clarity
    "-maxrate", "2500k",
    "-bufsize", "5000k",
    "-pix_fmt", "yuv420p",
    "-map", "0:a",
    "-c:a", "aac",
    "-b:a", "128k",
    "-f", "flv",
    rtmp_url
]

def log_reader(pipe):
    with open(ffmpeg_log, "w") as f:
        for line in iter(pipe.readline, b''):
            msg = line.decode(errors='replace')
            print(f"[FFmpeg] {msg}", end='', flush=True)
            f.write(msg)

print(f"🚀 Launching 720x1280 Filipino Stream: {time.strftime('%H:%M:%S')}")

try:
    process = subprocess.Popen(
        ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # Merge stderr into stdout for easier logging
        bufsize=1
    )

    # Correct Threading: Passing the pipe to the thread
    thread = threading.Thread(target=log_reader, args=(process.stdout,))
    thread.daemon = True
    thread.start()

    process.wait()
    print(f"🏁 Process exited with code {process.returncode}")

except Exception as e:
    print(f"❌ Critical Error: {e}")
