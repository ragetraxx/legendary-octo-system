#!/bin/bash

# Configuration
AUDIO_URL="https://stream.zeno.fm/q1n2wyfs7x8uv"
RTMP_URL=${RTMP_URL:-""}  # Get RTMP URL from environment variable

if [[ -z "$RTMP_URL" ]]; then
    echo "Error: RTMP_URL environment variable is not set."
    exit 1
fi

# Start FFmpeg with improved buffer settings and error handling
ffmpeg -re -i "$AUDIO_URL" \
       -c:v libx264 -preset ultrafast -tune zerolatency -b:v 2000k -g 30 \
       -c:a aac -b:a 128k -strict experimental -bufsize 2000k \
       -f flv "$RTMP_URL" 2>&1 | tee ffmpeg_log.txt

if [ $? -ne 0 ]; then
    echo "FFmpeg encountered an error. Check ffmpeg_log.txt for details."
    exit 1
fi
