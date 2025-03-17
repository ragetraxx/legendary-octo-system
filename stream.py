import subprocess

# Stream Source
AUDIO_URL = "https://stream.zeno.fm/q1n2wyfs7x8uv"
BACKGROUND_IMAGE = "background.png"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"

# FFmpeg Command (Simplified & Fixed)
ffmpeg_cmd = [
    "ffmpeg", "-re",
    "-i", AUDIO_URL,  # Input Audio Stream
    "-loop", "1", "-i", BACKGROUND_IMAGE,  # Background Image
    "-filter_complex",
    "[1:v]scale=1280:720[bg];"  # Scale Background
    "[0:a]showcqt=s=1280x720:fps=30:count=10:bar_g=3[visual];"  # Fullscreen Visualizer
    "[bg][visual]overlay=0:0[out]",  # Overlay Visualizer on Background
    "-map", "[out]", "-map", "0:a",
    "-c:v", "libx264", "-tune", "stillimage", "-b:v", "1500k", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", RTMP_URL  # Output to RTMP
]

# Run FFmpeg
subprocess.run(ffmpeg_cmd)
