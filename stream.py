import os
import re
import subprocess
import requests
from bs4 import BeautifulSoup

# Configuration
zeno_station_url = "https://zeno.fm/radio/ragemusicph/"
rtmp_url = os.getenv("RTMP_URL")  # Your RTMP URL, set this in GitHub Secrets
background_img = "background.png"
logo_img = "logo.png"
ffmpeg_log = "ffmpeg_output.log"

if not rtmp_url:
    print("❌ Error: RTMP_URL environment variable is not set.")
    exit(1)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://zeno.fm/"
}

def get_stream_url():
    print("🔎 Fetching stream URL from Zeno.fm page...")
    resp = requests.get(zeno_station_url, headers=HEADERS)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch Zeno.fm page, status code: {resp.status_code}")

    soup = BeautifulSoup(resp.text, "html.parser")

    # Look for the player data in the page scripts or audio tags
    # Zeno.fm typically embeds the stream URL inside a JavaScript variable or audio src

    # Try to find <audio> tag with src containing stream url
    audio_tag = soup.find("audio")
    if audio_tag and audio_tag.has_attr("src"):
        stream_url = audio_tag["src"]
        print(f"✅ Found stream URL from audio tag: {stream_url}")
        return stream_url

    # Fallback: search the page source for URLs matching the stream pattern
    match = re.search(r'https://stream-\d+\.zeno\.fm/[\w\d]+.*?\.mp3\?zt=[\w\-._~%]+', resp.text)
    if match:
        stream_url = match.group(0)
        print(f"✅ Found stream URL from page regex: {stream_url}")
        return stream_url

    raise Exception("❌ Could not find stream URL on the page")

stream_url = None
try:
    stream_url = get_stream_url()
except Exception as e:
    print(e)
    exit(1)

# Build FFmpeg command with user-agent and referer headers
ffmpeg_cmd = [
    "ffmpeg",
    "-re",
    "-user_agent", HEADERS["User-Agent"],
    "-headers", f"Referer: {HEADERS['Referer']}\r\n",
    "-i", stream_url,
    "-loop", "1", "-i", background_img,
    "-i", logo_img,
    "-filter_complex",
    "[0:a]avectorscope=s=1280x720:r=30,format=rgba,hue=h='mod(360*t/15,360)'[viz];"
    "[viz]scale=w=1280:h=720:eval=frame[exp_viz];"
    "[1:v]scale=1280:720[bg];"
    "[2:v]scale=200:200[logo];"
    "[bg][exp_viz]overlay=x='(W-w)/2':y='(H-h)/2'[bgviz];"
    "[bgviz][logo]overlay="
    "x='abs(mod(200*t, (W-w)*2) - (W-w))':"
    "y='abs(mod(150*t, (H-h)*2) - (H-h))'[out]",
    "-map", "[out]", "-c:v", "libx264", "-preset", "ultrafast",
    "-tune", "zerolatency", "-b:v", "1000k",
    "-map", "0:a", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
    "-f", "flv", rtmp_url
]

try:
    with open(ffmpeg_log, "w") as log_file:
        print("🚀 Starting FFmpeg stream...")
        process = subprocess.Popen(ffmpeg_cmd, stderr=log_file, stdout=log_file)
        process.wait()
        print("✅ FFmpeg process ended.")
except FileNotFoundError:
    print("❌ FFmpeg not found. Install it and make sure it's in your PATH.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
