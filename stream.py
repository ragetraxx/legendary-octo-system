import subprocess

# Streaming Credentials
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"

# Background Image
background_img = "background.png"

# FFmpeg command
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,  # Audio source
    "-loop", "1", "-i", background_img,  # Background image
    "-vf", "scale=1280:720",
    "-c:v", "libx264", "-tune", "stillimage", "-b:v", "1500k", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", rtmp_url  # RTMP Output
]

# Run the FFmpeg command
try:
    subprocess.run(ffmpeg_cmd, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
