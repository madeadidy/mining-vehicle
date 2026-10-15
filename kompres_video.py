import cv2
import os

input_path = "videos/mining_01.mp4"
output_path = "videos/mining_01_lite.mp4"

cap = cv2.VideoCapture(input_path)

# Ambil properti video asli
fps_asli = cap.get(cv2.CAP_PROP_FPS)
target_fps = fps_asli / 2  # Kita kurangi setengah FPS-nya biar ukuran file separuh lebih ringan

# Target resolusi (sama persis dengan yang dipakai di main.py)
width, height = 640, 360

# Gunakan codec mp4v untuk kompresi
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, target_fps, (width, height))

# Batasi durasi (Misal: maksimal 60 detik pertama saja agar pas untuk looping PoC)
max_durasi_detik = 60
max_frames = int(fps_asli * max_durasi_detik)

frame_count = 0
print("Sedang mengompres video... Mohon tunggu sebentar.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret or frame_count > max_frames:
        break
        
    frame_count += 1
    
    # Ambil hanya frame genap (menurunkan FPS setengahnya)
    if frame_count % 2 != 0:
        continue
        
    # Kecilkan resolusi
    frame_resized = cv2.resize(frame, (width, height))
    out.write(frame_resized)

cap.release()
out.release()

ukuran_baru = os.path.getsize(output_path) / (1024 * 1024)
print(f"Selesai! Video baru disimpan di: {output_path}")
print(f"Ukuran baru: {ukuran_baru:.2f} MB")