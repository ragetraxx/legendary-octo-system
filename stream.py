import os
import subprocess
import threading
import time
import sys

# === Configuration ===
stream_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url    = os.getenv("RTMP_URL")
background_img = "background.png"  # Should exist and be \~720x1280+
logo_img    = "logo.png"
ffmpeg_log  = "ffmpeg_output.log"

if not rtmp_url:
    print("❌ Error: RTMP_URL environment variable is not set.")
    sys.exit(1)

# === FFmpeg Command ===
ffmpeg_cmd = [
    "ffmpeg",
    "-re",
    "-i", stream_url,
    "-loop", "1", "-i", background_img,
    "-i", logo_img,
    "-filter_complex",
    "[0:a]asplit=2[aspec][abeat];"
    "[aspec]showfreqs="
    "s=720x820:"
    "mode=bar:"
    "colors=#9933ff|#3366ff|#00ccff|#33ff99|#ffff66|#ff4444:"
    "ascale=log:"
    "fscale=sqrt:"
    "win_func=gauss:"
    "orientation=vertical:"
    "legend=disabled:"
    "averager=10:"
    "peaks=0"
    "[spec];"
    "[abeat]showvolume=r=25:f=peak:draw=full:s=720x180:transparency=0.4[vol];"
    "[1:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:black[bg];"
    "[2:v]scale=220:-1[logo];"
    "[bg][spec]overlay=0:(H-h-60):format=auto[bgsp];"
    "[bgsp][vol]overlay=0:(H-h-20):format=auto[bgspv];"
    "[bgspv]format=rgba,geq=lum='lum(X,Y)*(1+0.7*A)':a='a(X,Y)*(1+0.5*A)'[pulsed];"
    "[pulsed]drawbox=x=W-320:y=200:w=300:h=200:t=fill:c=black@0.6[boxed];"
    "[boxed]drawtext=fontcolor=white:fontsize=28:borderw=2:bordercolor=black@0.6:x=W-300:y=240:text='Now Playing\\: %{metadata\\:icy-title}':expansion=normal:reload=1[txt];"
    "[txt][logo]overlay=x='abs(mod(100*t,(W-w)*2)-(W-w))':y='abs(mod(70*t,(H-h)*2)-(H-h))',format=yuv420p[out]",

    "-map", "[out]",
    "-map", "0:a",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-b:v", "2800k",
    "-maxrate", "2800k",
    "-bufsize", "5600k",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "128k",
    "-f", "flv",
    rtmp_url
]

def log_reader(pipe):
    with open(ffmpeg_log, "a", encoding="utf-8") as f:
        for line in iter(pipe.readline, ''):
            print(f"[FFmpeg] {line}", end='', flush=True)
            f.write(line)

print(f"🚀 Starting fixed Winamp-style visualizer + Now Playing → {time.strftime('%Y-%m-%d %H:%M:%S')}")

try:
    process = subprocess.Popen(
        ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        encoding='utf-8',
        errors='replace'
    )

    thread = threading.Thread(target=log_reader, args=(process.stdout,))
    thread.daemon = True
    thread.start()

    return_code = process.wait()
    print(f"🏁 FFmpeg exited with code {return_code}")

except Exception as e:
    print(f"❌ Critical error: {e}")
    sys.exit(1)
