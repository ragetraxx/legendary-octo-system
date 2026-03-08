import os
import subprocess
import threading
import time
import sys

# === Configuration ===
stream_url = "https://stream.zeno.fm/q1n2wyfs7x8uv"
rtmp_url    = os.getenv("RTMP_URL")
background_img = "background.png"  # Should be at least 720x1280 or larger
logo_img    = "logo.png"
ffmpeg_log  = "ffmpeg_output.log"

if not rtmp_url:
    print("❌ Error: RTMP_URL environment variable is not set.")
    sys.exit(1)

# === FFmpeg Command - Winamp-style spectrum bars (vertical layout) ===
ffmpeg_cmd = [
    "ffmpeg",
    "-re",
    "-i", stream_url,
    "-loop", "1", "-i", background_img,
    "-i", logo_img,
    "-filter_complex",

    # ───────────────────────────────────────────────────────────────
    # 1. Split audio → one for spectrum, one for beat pulse detection
    "[0:a]asplit=2[aspec][abeat];"

    # 2. Classic Winamp-style frequency bars (showfreqs in bar mode)
    #    - log scale + sqrt helps low-end (808/kick) visibility
    #    - colors go from purple→blue→cyan→green→yellow→red (classic vibe)
    "[aspec]showfreqs="
    "s=720x820:"                    # tall area for bars
    "mode=bar:"
    "colors=#9933ff|#3366ff|#00ccff|#33ff99|#ffff66|#ff4444:"  # purple to red
    "scale=log:"
    "fscale=sqrt:"                  # boost low frequencies
    "win_func=gauss:"
    "orientation=vertical:"
    "legend=disabled:"
    "averager=10:"                  # smooths a bit (less jitter)
    "peaks=1:peakf=0.8:peak持久=0.92[spec];"   # gentle peak falloff

    # 3. Quick beat envelope (makes background/overall pulse on kicks)
    "[abeat]showvolume="
    "r=25:"
    "f=peak:"
    "draw=full:"
    "s=720x180:"
    "transparency=0.4[vol];"

    # 4. Background - scale & pad to exactly 720x1280
    "[1:v]scale=720:1280:force_original_aspect_ratio=decrease,"
    "pad=720:1280:(ow-iw)/2:(oh-ih)/2: black[bg];"

    # 5. Logo scaling
    "[2:v]scale=220:-1[logo];"

    # 6. Composite layers:
    #    bg → spectrum at bottom → volume glow overlay → floating logo
    "[bg][spec]overlay=0:(H-h-60):format=auto[bgsp];"          # spectrum near bottom
    "[bgsp][vol]overlay=0:(H-h-20):format=auto[bgspv];"        # subtle volume glow
    "[bgspv]format=rgba,"
    "geq=lum='lum(X,Y)*(1+0.7*A)':a='a(X,Y)*(1+0.5*A)'[pulsed];"   # pulse whole frame on beat
    "[pulsed][logo]overlay="
    "x='abs(mod(100*t,(W-w)*2)-(W-w))':"
    "y='abs(mod(70*t,(H-h)*2)-(H-h))',"
    "format=yuv420p[out]",

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
    with open(ffmpeg_log, "w") as f:
        for line in iter(pipe.readline, ''):
            print(f"[FFmpeg] {line}", end='', flush=True)
            f.write(line)

print(f"🚀 Launching Winamp-style 720x1280 stream: {time.strftime('%H:%M:%S')}")

try:
    process = subprocess.Popen(
        ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        encoding='utf-8', errors='replace'
    )

    thread = threading.Thread(target=log_reader, args=(process.stdout,))
    thread.daemon = True
    thread.start()

    process.wait()
    print(f"🏁 Process exited with code {process.returncode}")

except Exception as e:
    print(f"❌ Critical Error: {e}")
    sys.exit(1)
