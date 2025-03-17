import subprocess

# Stream and output settings
AUDIO_URL = "https://stream.zeno.fm/q1n2wyfs7x8uv"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"
BACKGROUND_IMAGE = "background.png"

# FFmpeg command for full-screen visualizer without clock
ffmpeg_cmd = [
    "ffmpeg", "-re",
    "-i", AUDIO_URL,  
    "-loop", "1", "-i", BACKGROUND_IMAGE,  
    "-filter_complex",
    "[1:v]scale=1280:720[bg];"
    "[0:a]showcqt=s=1280x720:fps=30:count=10:bar_g=0.5[visual];"  # Full-screen visualizer
    "[bg][visual]blend=all_mode='screen'[out]",  # Overlay visualizer on background
    "-map", "[out]", "-map", "0:a",
    "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
    "-b:v", "1000k", "-bufsize", "1000k", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", RTMP_URL
]

# Run FFmpeg process
subprocess.run(ffmpeg_cmd)
