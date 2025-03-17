import subprocess

# Configuration
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url = "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"  # Update if needed
logo_img = "logo.png"

# Updated FFmpeg command
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,
    "-filter_complex",
    "[0:a]avectorscope=s=1280x720:rate=30:rc=1:gc=1:bc=1[v]; "
    "[1:v]scale=150:150,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(gt(sqrt(pow(X-75,2)+pow(Y-75,2)),75),0,a(X,Y))'[logo]; "
    "[v][logo]overlay=x=(W-w)/2:y=(H-h)/2[out]",
    "-map", "[out]",
    "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-b:v", "1000k",
    "-pix_fmt", "yuv420p", "-bufsize", "500k", "-g", "30", "-maxrate", "1000k",
    "-map", "0:a", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", rtmp_url
]

# Run FFmpeg process with logging
try:
    with open("stream.log", "w") as log_file:
        process = subprocess.Popen(ffmpeg_cmd, stderr=log_file, stdout=log_file)
    print("FFmpeg stream started. Check 'stream.log' for details.")
except FileNotFoundError:
    print("Error: FFmpeg not found. Ensure it is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
