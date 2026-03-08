import os
import subprocess
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

# === FFmpeg Command for 1280x720 Landscape ===
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", stream_url,
    "-loop", "1", "-re", "-i", background_img,
    "-loop", "1", "-re", "-i", logo_img,
    "-filter_complex",
    "[0:a]asplit=3[aspec][abeat][aout];"
    # Full-width visualizer (1280x200)
    "[aspec]showfreqs=s=1280x200:mode=bar,transpose=0[spec];"
    # Volume meter (300x100)
    "[abeat]showvolume=w=300:h=100:r=25:t=0[vol];"
    # Background scaled to 1280x720
    "[1:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720[bg];"
    "[2:v]scale=200:-1[logo];"
    # Overlay visualizer at the bottom (y=520, because 720 - 200 = 520)
    "[bg][spec]overlay=0:520[bgsp];"
    # Overlay volume meter at bottom-right (980, 620)
    "[bgsp][vol]overlay=980:620[bgspv];"
    # Text box for "Now Playing"
    "[bgspv]drawbox=x=20:y=20:w=250:h=80:t=fill:c=black@0.6[boxed];"
    f"[boxed]drawtext=fontfile={font_path}:fontcolor=white:fontsize=24:x=40:y=45:text='Now Playing'[txt];"
    # Logo movement within landscape bounds
    "[txt][logo]overlay=x='abs(mod(100*t,1000))':y='abs(mod(50*t,500))',format=yuv420p[v_out]",
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
