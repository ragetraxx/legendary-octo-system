import subprocess

# Define input sources
background_img = "background.png"  # Your uploaded background image
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"  # Your audio stream
rtmp_url = "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"  # RTMP output

# FFmpeg command to stream
ffmpeg_cmd = [
    "ffmpeg",
    "-re", "-i", audio_url,  # Audio input
    "-loop", "1", "-i", background_img,  # Background image

    # Overlay Clock and Audio Visualizer
    "-filter_complex",
    "[1:v]scale=1280:720[bg];"
    "[bg]drawtext=text='%{localtime\\:%H\\:%M\\:%S}': fontcolor=white: fontsize=50: x=1000: y=30[clock];"
    "[0:a]showcqt=s=1280x200:fps=30:count=40[visual];"
    "[clock][visual]overlay=x=0:y=520[out]",

    "-map", "[out]", "-map", "0:a",  # Video and audio mapping
    "-c:v", "libx264", "-tune", "stillimage", "-b:v", "1500k", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-f", "flv", rtmp_url  # Stream to RTMP
]

# Run FFmpeg process
subprocess.run(ffmpeg_cmd)
