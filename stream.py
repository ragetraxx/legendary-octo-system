import subprocess

# Configuration
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"
logo_img = "logo.png"

# FFmpeg command with a generated background, visualizer, and logo
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,
    "-f", "lavfi", "-t", "99999", "-i", "color=s=1280x720:c=black:r=30",  # Black background
    "-loop", "1", "-i", logo_img,  # Logo input
    "-filter_complex",
    "[0:a]avectorscope=s=1280x720:rate=30:rc=1:gc=1:bc=1[v]; "  # Generate visualizer
    "[1:v][v]overlay=0:0[bg_visual]; "  # Overlay visualizer on black background
    "[2:v]scale=200:200[logo]; "  # Resize logo to 200x200
    "[bg_visual][logo]overlay=x=(W-w)/2:y=20[out]",  # Overlay logo on visualizer
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-b:v", "1000k",
    "-map", "0:a", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", rtmp_url
]

try:
    process = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    print("FFmpeg stream started with visualizer and logo.")
    for line in process.stderr:
        print(line.decode(), end="")
except FileNotFoundError:
    print("Error: FFmpeg not found. Ensure it is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
