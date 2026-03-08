import os
import subprocess
import threading
import time
import sys

# === Configuration ===
stream_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = os.getenv("RTMP_URL")
background_img = "background.png"
logo_img = "logo.png"
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

if not rtmp_url:
    print("❌ Error: RTMP_URL environment variable is not set.")
    sys.exit(1)

# === FFmpeg Command ===
# Removed 'reload=1' and simplified drawtext to prevent file-read errors
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", stream_url,
    "-loop", "1", "-re", "-i", background_img,
    "-loop", "1", "-re", "-i", logo_img,
    "-filter_complex",
    "[0:a]asplit=3[aspec][abeat][aout];"
    "[aspec]showfreqs=s=820x720:mode=bar,transpose=1[spec];"
    "[abeat]showvolume=w=720:h=100:r=25:t=0[vol];"
    "[1:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280[bg];"
    "[2:v]scale=220:-1[logo];"
    "[bg][spec]overlay=0:560[bgsp];"
    "[bgsp][vol]overlay=0:1160[bgspv];"
    "[bgspv]drawbox=x=400:y=200:w=300:h=200:t=fill:c=black@0.6[boxed];"
    f"[boxed]drawtext=fontfile={font_path}:fontcolor=white:fontsize=24:x=420:y=240:text='Now Playing':shadowx=2:shadowy=2[txt];"
    "[txt][logo]overlay=x='abs(mod(100*t,400))':y='abs(mod(70*t,900))',format=yuv420p[v_out]",
    "-map", "[v_out]", "-map", "[aout]",
    "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency",
    "-b:v", "2800k", "-maxrate", "2800k", "-bufsize", "5600k",
    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-f", "flv", rtmp_url
]

try:
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in iter(process.stdout.readline, ''):
        print(f"[FFmpeg] {line.strip()}")
except Exception as e:
    print(f"❌ Error: {e}")
