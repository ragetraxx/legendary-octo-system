import cv2
import numpy as np
import ffmpeg
import time
import datetime
import pyaudio
import wave
import struct
import math
import subprocess

# Constants
WIDTH, HEIGHT = 1920, 1080  # 1080p resolution
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
LOGO_PATH = "logo.png"  # Place your logo in the same directory
FONT = cv2.FONT_HERSHEY_SIMPLEX
AUDIO_DEVICE_INDEX = None  # Set to None for default audio input

# Gradient background
gradient = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
for y in range(HEIGHT):
    color = (255 * y // HEIGHT, 128, 255 - (255 * y // HEIGHT))  # Purple-pink gradient
    gradient[y, :] = color

# Load logo
logo = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)
if logo is not None:
    logo_height, logo_width = logo.shape[:2]
    logo_x = (WIDTH - logo_width) // 2
    logo_y = 50  # Position logo at the top

# Audio setup
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

def get_audio_levels():
    data = stream.read(CHUNK, exception_on_overflow=False)
    unpacked_data = struct.unpack(str(CHUNK) + "h", data)
    levels = [abs(sample) / 32768.0 for sample in unpacked_data]
    return sum(levels) / len(levels)  # Normalize volume

# Circular visualizer
def draw_visualizer(frame, volume):
    num_circles = 12
    max_radius = 150
    angle_step = 360 // num_circles

    for i in range(num_circles):
        angle = math.radians(i * angle_step)
        radius = int(max_radius * volume) + 20  # Scale radius with volume
        x = int(CENTER_X + radius * math.cos(angle))
        y = int(CENTER_Y + radius * math.sin(angle))
        cv2.circle(frame, (x, y), int(10 + volume * 20), (0, 255, 0), -1)

# Start FFmpeg streaming
ffmpeg_command = [
    "ffmpeg",
    "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "bgr24",
    "-r", "30",
    "-i", "-",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-b:v", "2000k",
    "-g", "30",
    "-f", "flv",
    "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"
]

ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

# Main loop
while True:
    frame = gradient.copy()

    # Draw time
    now = datetime.datetime.now().strftime("%I:%M:%S %p")
    text_size = cv2.getTextSize(now, FONT, 2, 5)[0]
    text_x = (WIDTH - text_size[0]) // 2
    text_y = CENTER_Y
    cv2.putText(frame, now, (text_x, text_y), FONT, 2, (255, 255, 255), 5)

    # Draw visualizer
    volume = get_audio_levels()
    draw_visualizer(frame, volume)

    # Overlay logo
    if logo is not None:
        frame[logo_y:logo_y + logo_height, logo_x:logo_x + logo_width] = logo[:, :, :3]

    # Send frame to FFmpeg
    ffmpeg_process.stdin.write(frame.tobytes())

# Cleanup
stream.stop_stream()
stream.close()
audio.terminate()
ffmpeg_process.stdin.close()
ffmpeg_process.wait()
cv2.destroyAllWindows()
