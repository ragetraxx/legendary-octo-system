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

# === Updated FFmpeg Command ===
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", stream_url,
    "-loop", "1", "-re", "-i", background_img,
    "-loop", "1", "-re", "-i", logo_img,
    "-filter_complex",
    # 1. Split incoming audio stream for processing and actual playback
    "[0:a]asplit=2[audio_vis][aout];"
    
    # 2. Generate a 500x500 circular vector visualizer that pulsates with the beat
    "[audio_vis]avectorscope=s=500x500:m=mirror:zoom=2:rc=40:gc=160:bc=240[v_ring];"
    
    # 3. Format and size assets for 1280x720 output
    "[1:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720[bg];"
    "[2:v]scale=200:200:force_original_aspect_ratio=decrease[logo];"
    
    # 4. Burn "Now Playing" box onto the background
    "[bg]drawbox=x=20:y=20:w=250:h=80:t=fill:c=black@0.6[boxed];"
    f"[boxed]drawtext=fontfile={font_path}:fontcolor=white:fontsize=24:x=40:y=45:text='Now Playing'[txt];"
    
    # 5. Overlay the 500x500 pulsating ring dead-center
    # X: (1280 - 500) / 2 = 390 | Y: (720 - 500) / 2 = 110
    "[txt][v_ring]overlay=390:110:shortest=1[bg_with_ring];"
    
    # 6. Overlay the 200x200 logo perfectly in the center of the ring
    # X: (1280 - 200) / 2 = 540 | Y: (720 - 200) / 2 = 260
    "[bg_with_ring][logo]overlay=540:260,format=yuv420p[v_out]",
    
    # Map video and audio to final output
    "-map", "[v_out]", "-map", "[aout]",
    "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency",
    "-b:v", "2800k", "-maxrate", "2800k", "-bufsize", "5600k",
    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-f", "flv", rtmp_url
]

try:
    print("🚀 Starting RTMP stream with centered logo and pulsating visualizer...")
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in iter(process.stdout.readline, ''):
        print(f"[FFmpeg] {line.strip()}")
except Exception as e:
    print(f"❌ Error: {e}")
