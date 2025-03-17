ffmpeg -f rawvideo -pixel_format bgr24 -video_size 1920x1080 -framerate 30 -i - \
       -i "https://stream.zeno.fm/q1n2wyfs7x8uv" -c:v libx264 -preset ultrafast -b:v 3000k -g 60 \
       -c:a aac -b:a 128k -strict experimental -f flv \
       "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"
