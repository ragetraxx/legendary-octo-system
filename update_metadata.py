import requests
import time

URL = "https://stream.zeno.fm/q1n2wyfs7x8uv"

def fetch_metadata():
    headers = {"Icy-MetaData": "1"}
    response = requests.get(URL, headers=headers, stream=True)

    if "StreamTitle='" in response.text:
        start = response.text.index("StreamTitle='") + len("StreamTitle='")
        end = response.text.index("';", start)
        title_artist = response.text[start:end]
        
        if " - " in title_artist:
            artist, title = title_artist.split(" - ", 1)
        else:
            artist, title = "Unknown Artist", title_artist

        with open("title.txt", "w") as t:
            t.write(title)
        with open("artist.txt", "w") as a:
            a.write(artist)

while True:
    fetch_metadata()
    time.sleep(30)  # Update every 30 seconds 
