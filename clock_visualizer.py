import cv2
import numpy as np
import ffmpeg
import datetime
import pyaudio

# Constants
WIDTH, HEIGHT = 1920, 1080
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
LOGO_PATH = "logo.png"
FONT = cv2.FONT_HERSHEY_SIMPLEX

# Gradient background
gradient = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
for y in range(HEIGHT):
    color = (255 * y // HEIGHT, 128, 255 - (255 * y // HEIGHT))  # Purple-pink gradient
    gradient[y, :] = color

# Load logo
logo = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)
if logo is None:
    print("Warning: Logo image not found. Proceeding without logo.")
else:
    logo_height, logo_width = logo.shape[:2]
    logo_x = (WIDTH - logo_width) // 2
    logo_y = 50  # Position logo at the top

# FFmpeg process
output_url = "rtmp://ssh101.bozztv.com:1935/ssh101/ragemusicph"

ffmpeg_cmd = (
    ffmpeg
    .input('pipe:', format='rawvideo', pix_fmt='bgr24', s=f'{WIDTH}x{HEIGHT}')
    .output(output_url, format='flv', vcodec='libx264', pix_fmt='yuv420p', r=30)
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

# Video loop
while True:
    frame = gradient.copy()
    now = datetime.datetime.now().strftime("%H:%M:%S")
    cv2.putText(frame, now, (CENTER_X - 100, CENTER_Y), FONT, 3, (255, 255, 255), 5)

    # Overlay logo if available
    if logo is not None:
        frame[logo_y:logo_y+logo_height, logo_x:logo_x+logo_width] = logo

    ffmpeg_cmd.stdin.write(frame.tobytes())

ffmpeg_cmd.stdin.close()
ffmpeg_cmd.wait()
