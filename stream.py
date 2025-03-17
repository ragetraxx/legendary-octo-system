import os
import subprocess

# Stream and output settings
AUDIO_URL = "https://stream.zeno.fm/q1n2wyfs7x8uv"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"
BACKGROUND_IMAGE = "background.png"

# FFmpeg command
ffmpeg_cmd = [
    "ffmpeg", "-re",
    "-probesize", "32", "-analyzeduration", "0",
    "-i", AUDIO_URL,
    "-loop", "1", "-i", BACKGROUND_IMAGE,
    "-filter_complex",
    "[1:v]scale=1280:720[bg];"
    "[bg]drawtext=text='%{localtime\\:%H\\:%M\\:%S}':fontcolor=white:fontsize=50:x=1000:y=30[clock];"
    "[0:a]avectorscope=s=1280x200:rate=25:rc=0:gc=0:bc=255[visual];"
    "[clock][visual]overlay=x=0:y=520[out]",
    "-map", "[out]", "-map", "0:a",
    "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
    "-b:v", "800k", "-bufsize", "800k", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "96k", "-ar", "44100",
    "-f", "flv", RTMP_URL
]

# Run FFmpeg process
subprocess.run(ffmpeg_cmd)
