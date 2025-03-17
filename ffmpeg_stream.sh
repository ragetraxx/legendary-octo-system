#!/bin/bash

# Configuration
AUDIO_URL="https://stream.zeno.fm/q1n2wyfs7x8uv"
RTMP_URL="rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"

# Start FFmpeg with improved buffer settings and error handling
ffmpeg -re -i "$AUDIO_URL" \
       -c:v libx264 -preset ultrafast -tune zerolatency -b:v 2000k -g 30 \
       -c:a aac -b:a 128k -strict experimental -bufsize 2000k \
       -f flv "$RTMP_URL" 2>&1 | tee ffmpeg_log.txt

if [ $? -ne 0 ]; then
    echo "FFmpeg encountered an error. Check ffmpeg_log.txt for details."
    exit 1
fi
