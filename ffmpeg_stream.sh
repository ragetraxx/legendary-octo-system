#!/bin/bash

ffmpeg -re \
       -i "https://stream.zeno.fm/q1n2wyfs7x8uv" \
       -c:v libx264 -preset ultrafast -tune zerolatency -b:v 2000k -g 30 \
       -c:a aac -b:a 128k -strict experimental -bufsize 4000k \
       -f flv "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"
