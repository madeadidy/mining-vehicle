import cv2
import os

VIDEO_PATH = "videos/mining_01.mp4"
OUTPUT_DIR = "frames"

os.makedirs(OUTPUT_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("Gagal membuka video.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps

print(f"FPS           : {fps}")
print(f"Total frame   : {total_frames}")
print(f"Durasi        : {duration:.2f} detik")

# Ambil 1 frame setiap 1 detik
interval = int(fps)

frame_number = 0
saved = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    if frame_number % interval == 0:
        filename = os.path.join(
            OUTPUT_DIR,
            f"frame_{saved:05d}.jpg"
        )

        cv2.imwrite(filename, frame)
        saved += 1

    frame_number += 1

cap.release()

print(f"\nSelesai.")
print(f"Frame disimpan: {saved}")