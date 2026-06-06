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
filter_str = (
    "[0:a]asplit=2[audio_vis][aout];"
    "[audio_vis]avectorscope=s=400x400:m=polar:zoom=3:rc=20:gc=180:bc=255:rf=10:gf=40:bf=80[v_ring];"
    "[1:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720[bg];"
    "[2:v]scale=220:220:force_original_aspect_ratio=decrease[logo];"
    "[bg]drawbox=x=20:y=20:w=250:h=80:t=fill:c=black@0.6[boxed];"
    f"[boxed]drawtext=fontfile={font_path}:fontcolor=white:fontsize=24:x=40:y=45:text='Now Playing'[txt];"
    "[txt][v_ring]overlay=440:160:shortest=1[bg_with_ring];"
    "[bg_with_ring][logo]overlay=530:250,format=yuv420p[v_out]"
)

# === Anti-Lag FFmpeg Command Configuration ===
ffmpeg_cmd = [
    "ffmpeg",
    # 1. Allocate large thread queues for inputs to absorb network hiccups
    "-thread_queue_size", "2048",
    "-i", stream_url,
    
    "-thread_queue_size", "1024",
    "-loop", "1", "-i", background_img,
    
    "-thread_queue_size", "1024",
    "-loop", "1", "-i", logo_img,
    
    # 2. Filter Graph processing
    "-filter_complex", filter_str,
    
    # 3. Stream output mapping
    "-map", "[v_out]", 
    "-map", "[aout]",
    
    # 4. Video encoding optimizations (Crucial for Anti-Lag)
    "-c:v", "libx264", 
    "-preset", "veryfast",           # 'veryfast' or 'superfast' is more stable for long streams than ultrafast
    "-tune", "zerolatency", 
    "-r", "30",                      # Force lock to 30 frames per second
    "-g", "60",                      # Force keyframe every 60 frames (Exactly 2 seconds at 30fps)
    "-keyint_min", "60",             # Prevents FFmpeg from creating random extra keyframes
    "-sc_threshold", "0",            # Disables scene change detection (prevents random keyframe placement)
    
    # 5. Network & Bitrate Optimization
    "-b:v", "2000k",                 # 2000k is perfect for clear 720p 30fps without choking your upload speed
    "-maxrate", "2000k", 
    "-bufsize", "4000k",             # Buffer size is exactly 2x maxrate for steady data pacing
    "-pix_fmt", "yuv420p", 
    
    # 6. Audio encoding parameters
    "-c:a", "aac", 
    "-b:a", "128k", 
    "-ar", "44100",                  # Explicitly set audio sample rate for server compatibility
    
    # 7. Real-time stream delivery push
    "-f", "flv", 
    rtmp_url
]

try:
    print("🚀 Launching ultra-stabilized RTMP stream...")
    # added bufsize=1 to prevent Python from caching output lines 
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)
    for line in iter(process.stdout.readline, ''):
        print(f"[FFmpeg] {line.strip()}")
except Exception as e:
    print(f"❌ Error: {e}")
