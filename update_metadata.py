import requests
import time

URL = "https://stream.zeno.fm/q1n2wyfs7x8uv"

def fetch_metadata():
    try:
        headers = {"Icy-MetaData": "1"}
        response = requests.get(URL, headers=headers, stream=True)

        # Read metadata from response headers
        icy_metaint = int(response.headers.get("icy-metaint", 0))
        if icy_metaint == 0:
            print("No ICY metadata available.")
            return

        response.raw.read(icy_metaint)  # Skip audio data
        metadata = response.raw.read(255).decode(errors="ignore")

        if "StreamTitle='" in metadata:
            start = metadata.index("StreamTitle='") + len("StreamTitle='")
            end = metadata.index("';", start)
            title_artist = metadata[start:end]

            if " - " in title_artist:
                artist, title = title_artist.split(" - ", 1)
            else:
                artist, title = "Unknown Artist", title_artist

            with open("title.txt", "w") as t:
                t.write(title)
            with open("artist.txt", "w") as a:
                a.write(artist)

            print(f"Updated Metadata: {artist} - {title}")
    except Exception as e:
        print(f"Error fetching metadata: {e}")

while True:
    fetch_metadata()
    time.sleep(30)  # Update every 30 seconds
