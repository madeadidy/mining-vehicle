import os
from ultralytics import YOLO

# 1. Inisialisasi model YOLOv8 pretrained (otomatis terunduh saat pertama kali dijalankan)
model = YOLO('yolov8n.pt') 

# 2. Definisikan path folder relatif dari lokasi script dijalankan
INPUT_DIR = 'frames'
OUTPUT_DIR = 'outputs'

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 3. Kumpulkan semua file gambar dari folder frames
image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
print(f"Ditemukan {len(image_files)} frame untuk diproses.")

# 4. Jalankan deteksi secara batch untuk efisiensi
if image_files:
    image_paths = [os.path.join(INPUT_DIR, f) for f in image_files]
    
    # Menjalankan inferensi dan menyimpan hasilnya
    results = model.predict(
        source=image_paths, 
        save=True, 
        project=OUTPUT_DIR, 
        name='baseline_test', 
        exist_ok=True,
        conf=0.25 # Ambang batas minimum confidence score
    )
    print(f"\nProses selesai! Hasil deteksi beserta bounding box disimpan di: {OUTPUT_DIR}/baseline_test")
else:
    print("Tidak ada gambar yang ditemukan di folder frames/")