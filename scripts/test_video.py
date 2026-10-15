import os
from ultralytics import YOLO

MODEL_PATH = 'runs/detect/outputs/mining_model_v01-4/weights/best.pt'
VIDEO_INPUT = 'videos/mining_01.mp4'  
OUTPUT_DIR = 'outputs'

print(f"Memuat model dari: {MODEL_PATH}")
model = YOLO(MODEL_PATH)

print(f"Mulai memproses video (Mode Stream Hemat RAM): {VIDEO_INPUT}")

# Tambahkan stream=True agar RAM tidak jebol
results = model.predict(
    source=VIDEO_INPUT,
    save=True,               
    project=OUTPUT_DIR,
    name='video_test_v02',   # Aku ubah namanya agar tidak menimpa folder error tadi
    conf=0.5,                
    stream=True              # <--- INI KUNCI UTAMANYA
)

# Jika menggunakan stream=True, kita wajib melakukan looping agar videonya diproses
for r in results:
    pass 

print(f"\nSelesai! Video hasil deteksi bisa kamu lihat di folder: {OUTPUT_DIR}/video_test_v02")