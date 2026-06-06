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

# === Optimized Filter Graph ===
# avectorscope=m=polar forces the lines into a beautiful dynamic circle
filter_str = (
    "[0:a]asplit=2[audio_vis][aout];"
    "[audio_vis]avectorscope=s=400x400:m=polar:zoom=3:rc=20:gc=180:bc=255:rf=10:gf=40:bf=80[v_ring];"
    "[1:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720[bg];"
    "[2:v]scale=220:220:force_original_aspect_ratio=decrease[logo];"
    "[bg]drawbox=x=20:y=20:w=250:h=80:t=fill:c=black@0.6[boxed];"
    f"[boxed]drawtext=fontfile={font_path}:fontcolor=white:fontsize=24:x=40:y=45:text='Now Playing'[txt];"
    # Center the 400x400 Ring: X=(1280-400)/2 = 440 | Y=(720-400)/2 = 160
    "[txt][v_ring]overlay=440:160:shortest=1[bg_with_ring];"
    # Center the 220x220 Logo inside the ring: X=(1280-220)/2 = 530 | Y=(720-220)/2 = 250
    "[bg_with_ring][logo]overlay=530:250,format=yuv420p[v_out]"
)

# === Updated Anti-Buffering FFmpeg Command ===
ffmpeg_cmd = [
    "ffmpeg",
    "-re", 
    "-thread_queue_size", "1024",       # Prevents input buffer underflow drops
    "-i", stream_url,
    "-loop", "1", "-re", "-i", background_img,
    "-loop", "1", "-re", "-i", logo_img,
    "-filter_complex", filter_str,
    "-map", "[v_out]", 
    "-map", "[aout]",
    "-c:v", "libx264", 
    "-preset", "ultrafast", 
    "-tune", "zerolatency,animation",   # Tweaked tuning flags to process geometric visualizer matrices efficiently
    "-r", "30",                         # Enforce strict 30fps stream target
    "-g", "60",                         # Keyframe interval every 2 seconds (Crucial to eliminate server buffering)
    "-threads", "0",                    # Allow FFmpeg to multithread dynamically
    "-b:v", "1500k",                    # Slightly streamlined video bitrate for sustained live stability
    "-maxrate", "1500k", 
    "-bufsize", "3000k",
    "-pix_fmt", "yuv420p", 
    "-c:a", "aac", 
    "-b:a", "128k", 
    "-f", "flv", 
    rtmp_url
]

try:
    print("🚀 Launching stabilized RTMP stream with concentric circular visualizer...")
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in iter(process.stdout.readline, ''):
        print(f"[FFmpeg] {line.strip()}")
except Exception as e:
    print(f"❌ Error: {e}")
