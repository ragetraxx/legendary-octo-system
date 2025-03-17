import subprocess

# Configuration
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"
background_img = "background.png"
logo_img = "logo.png"

# FFmpeg command with enhanced blending, transparency, and animation
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,
    "-loop", "1", "-i", background_img,  # Background image
    "-loop", "1", "-i", logo_img,  # Logo image
    "-filter_complex",
    "[0:a]showcqt=s=1280x720:r=30:fullhd=1:bar_g=5:bar_v=5:fps=30:brightness=1.5:contrast=1.5[v]; "  # More vibrant visualizer
    "[1:v]scale=1280:720,format=rgba,fade=t=in:st=0:d=3:alpha=1[bg]; "  # Animated fade-in background
    "[bg][v]blend=all_mode='overlay':all_opacity=0.6[bg_visual]; "  # Soft overlay blending
    "[2:v]scale=250:-1[logo]; "  # Resize logo
    "[bg_visual][logo]overlay=x=(W-w)/2:y=20[out]",  # Logo centered at the top
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-b:v", "1000k",
    "-map", "0:a", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", rtmp_url
]

try:
    process = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    print("FFmpeg stream started with blended visualizer, animated background, and logo.")
    for line in process.stderr:
        print(line.decode(), end="")
except FileNotFoundError:
    print("Error: FFmpeg not found. Ensure it is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
