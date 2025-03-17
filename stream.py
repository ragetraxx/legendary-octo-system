import subprocess

# Streaming Credentials
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"

# Overlay Image
logo_img = "logo.png"

# FFmpeg command
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,  # Audio source
    "-filter_complex",
    "[0:a]showspectrum=s=1280x720:mode=line:color=white,format=rgba[v];"
    "[1:v]scale=150:150,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(gt(sqrt(pow(X-75,2)+pow(Y-75,2)),75),0,a(X,Y))'[logo];"
    "[v][logo]overlay=x=(W-w)/2:y=(H-h)/2[out]",
    "-map", "[out]",
    "-c:v", "libx264", "-tune", "stillimage", "-b:v", "1500k", "-pix_fmt", "yuv420p",
    "-map", "0:a",
    "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", rtmp_url  # RTMP Output
]

# Run the FFmpeg command
try:
    process = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE)
    _, stderr = process.communicate()
    if process.returncode != 0:
        print(f"FFmpeg Error (Return Code: {process.returncode}):")
        print(stderr.decode())
    else:
        print("FFmpeg stream started successfully.")

except FileNotFoundError:
    print("Error: FFmpeg not found. Ensure it is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

