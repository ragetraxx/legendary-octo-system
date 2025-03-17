import subprocess

# Configuration
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"
background_img = "background.png"
logo_img = "logo.png"

# FFmpeg command with background, visualizer, and logo
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,
    "-loop", "1", "-i", background_img,  # Background
    "-i", logo_img,  # Logo
    "-filter_complex",
    "[0:a]showspectrum=size=1280x720:mode=separate:color=intensity:scale=log:legend=0,format=rgba[viz];"  # Visualizer
    "[1:v]scale=1280:720[bg];"  # Scale background
    "[2:v]scale=525:539[logo];"  # Scale logo
    "[bg][viz]overlay=(W-w)/2:(H-h)/2[bgviz];"  # Overlay visualizer on background
    "[bgviz][logo]overlay=(W-w)/2:50[out]",  # Overlay logo
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-b:v", "1000k",
    "-map", "0:a", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", rtmp_url
]

# Run FFmpeg with logging
try:
    with open("ffmpeg_output.log", "w") as log_file:
        process = subprocess.Popen(ffmpeg_cmd, stderr=log_file, stdout=log_file)
        print("FFmpeg stream started.")
        process.wait()  # Keep the process running
except FileNotFoundError:
    print("Error: FFmpeg not found. Ensure it is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
