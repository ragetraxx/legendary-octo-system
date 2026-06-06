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

# === Low-Res Optimized Filter Graph (854x480 Canvas) ===
filter_str = (
    "[0:a]asplit=2[audio_vis][aout];"
    # Scaled visualizer down to 300x300 to match lower resolution
    "[audio_vis]avectorscope=s=300x300:m=polar:zoom=3:rc=20:gc=180:bc=255:rf=10:gf=40:bf=80[v_ring];"
    "[1:v]scale=854:480:force_original_aspect_ratio=increase,crop=854:480[bg];"
    # Scaled logo down to 160x160 to fit inside the smaller ring
    "[2:v]scale=160:160:force_original_aspect_ratio=decrease[logo];"
    "[bg]drawbox=x=20:y=20:w=250:h=80:t=fill:c=black@0.6[boxed];"
    f"[boxed]drawtext=fontfile={font_path}:fontcolor=white:fontsize=24:x=40:y=45:text='Now Playing'[txt];"
    # Center 300x300 Ring on 854x480: X=(854-300)/2 = 277 | Y=(480-300)/2 = 90
    "[txt][v_ring]overlay=277:90:shortest=1[bg_with_ring];"
    # Center 160x160 Logo on 854x480: X=(854-160)/2 = 347 | Y=(480-160)/2 = 160
    "[bg_with_ring][logo]overlay=347:160,format=yuv420p[v_out]"
)

# === High-Stability, Low-Quality FFmpeg Command ===
ffmpeg_cmd = [
    "ffmpeg",
    # Network Pre-Buffering & Auto-Reconnect Settings
    "-reconnect", "1",
    "-reconnect_at_eof", "1",
    "-reconnect_streamed", "1",
    "-reconnect_delay_max", "5",
    "-thread_queue_size", "4096",       # Doubled buffer size to cache more audio data
    "-i", stream_url,
    
    "-thread_queue_size", "1024",
    "-loop", "1", "-i", background_img,
    
    "-thread_queue_size", "1024",
    "-loop", "1", "-i", logo_img,
    
    "-filter_complex", filter_str,
    
    "-map", "[v_out]", 
    "-map", "[aout]",
    
    # Low-demand Video Encoding
    "-c:v", "libx264", 
    "-preset", "ultrafast",            # Least CPU usage possible
    "-tune", "zerolatency", 
    "-r", "25",                        # Dropped frame rate to 25fps to ease network load
    "-g", "50",                        # Keyframe interval every 2 seconds (50 frames at 25fps)
    "-keyint_min", "50",
    "-sc_threshold", "0",
    
    # Drastically lowered Bitrate Settings for smooth playback
    "-b:v", "1000k",                   # 1000k is lean and highly stable for 480p streams
    "-maxrate", "1000k", 
    "-bufsize", "2000k",               # Paces the data nicely over the connection
    "-pix_fmt", "yuv420p", 
    
    # Audio Settings
    "-c:a", "aac", 
    "-b:a", "96k",                     # Slightly lowered audio bitrate for maximum safety
    "-ar", "44100",
    
    "-f", "flv", 
    rtmp_url
]

try:
    print("🚀 Launching ultra-stable, light-weight 480p RTMP stream...")
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)
    for line in iter(process.stdout.readline, ''):
        print(f"[FFmpeg] {line.strip()}")
except Exception as e:
    print(f"❌ Error: {e}")
