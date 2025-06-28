import os
import subprocess
import threading
import time

# === Configuration ===
stream_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = os.getenv("RTMP_URL")
background_img = "background.png"
logo_img = "logo.png"
ffmpeg_log = "ffmpeg_output.log"
USE_H265 = False  # 🔁 Toggle H.265 here

# === Sanity Check ===
if not rtmp_url:
    print("❌ Error: RTMP_URL environment variable is not set.")
    exit(1)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://zeno.fm/"
}

# === Codec Settings ===
video_codec = "libx265" if USE_H265 else "libx264"
profile = "main" if USE_H265 else "high"
level = "3.2"

# === FFmpeg Command ===
ffmpeg_cmd = [
    "ffmpeg",
    "-re",
    "-user_agent", HEADERS["User-Agent"],
    "-headers", f"Referer: {HEADERS['Referer']}\r\n",
    "-i", stream_url,
    "-loop", "1", "-i", background_img,
    "-i", logo_img,
    "-filter_complex",
    "[0:a]avectorscope=s=1024x576:r=25,format=rgba,hue=h='mod(360*t/15,360)'[viz];"
    "[viz]scale=1024:576[exp_viz];"
    "[1:v]scale=1024:576[bg];"
    "[2:v]scale=150:150[logo];"
    "[bg][exp_viz]overlay=(W-w)/2:(H-h)/2[bgviz];"
    "[bgviz][logo]overlay="
    "x='abs(mod(100*t\\,(W-w)*2)-(W-w))':"
    "y='abs(mod(75*t\\,(H-h)*2)-(H-h))'[out]",
    "-map", "[out]",
    "-c:v", video_codec,
    "-profile:v", profile,
    "-level:v", level,
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-b:v", "1300k",
    "-maxrate", "1400k",
    "-bufsize", "1400k",
    "-pix_fmt", "yuv420p",
    "-map", "0:a",
    "-c:a", "aac",
    "-b:a", "160k",
    "-ac", "2",
    "-ar", "48000",
    "-f", "flv",
    rtmp_url
]

# === Threaded Logging Function ===
def tee_output_stream(stream, logfile_path):
    def stream_reader():
        with open(logfile_path, "w") as f:
            for line in iter(stream.readline, b''):
                decoded = line.decode(errors='replace')
                print(decoded, end='')  # Print to GitHub log
                f.write(decoded)
    return stream_reader

# === Heartbeat Logger ===
def heartbeat(process):
    while process.poll() is None:
        print(f"💓 Still streaming... {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        time.sleep(55)

# === Launch FFmpeg ===
print("🚀 Starting FFmpeg stream at 1024x576, High@L3.2...")

try:
    process = subprocess.Popen(
        ffmpeg_cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        bufsize=1
    )

    stderr_thread = threading.Thread(target=tee_output_stream(process.stderr, ffmpeg_log))
    heartbeat_thread = threading.Thread(target=heartbeat, args=(process,))

    stderr_thread.start()
    heartbeat_thread.start()

    process.wait()
    stderr_thread.join()
    heartbeat_thread.join()

    print("✅ FFmpeg process completed.")

except FileNotFoundError:
    print("❌ FFmpeg not found. Make sure it's installed and available in your PATH.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
