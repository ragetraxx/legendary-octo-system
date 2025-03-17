import os

# RTMP Streaming URL
rtmp_url = "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"

# Input Streams
audio_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
background_image = "background.png"
logo_image = "logo.png"

# FFmpeg Command
ffmpeg_cmd = f"""
ffmpeg -re -i "{audio_url}" \
-loop 1 -i "{background_image}" -i "{logo_image}" \
-filter_complex "[1:v]scale=1280:720[bg];[0:a]showcqt=s=1280x720:fps=30:count=10:bar_g=3[visual];[bg][visual]overlay=0:0[vis];[vis][2:v]overlay=W-w-20:20[out]" \
-map "[out]" -map "0:a" -c:v libx264 -tune stillimage -b:v 1500k -pix_fmt yuv420p \
-c:a aac -b:a 128k -ar 44100 -f flv "{rtmp_url}"
"""

# Run FFmpeg
os.system(ffmpeg_cmd)
