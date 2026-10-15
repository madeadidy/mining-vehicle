from ultralytics import YOLO

# 1. Load model pretrained YOLOv8 nano (paling ringan untuk PoC)
model = YOLO('yolov8n.pt')

# 2. Menjalankan proses training (fine-tuning)
print("Memulai proses training Custom Model Mining Vehicle...")
results = model.train(
    data='dataset/data.yaml',  # File konfigurasi yang baru saja kamu buat
    epochs=50,                 # Jumlah putaran belajar (50 cukup untuk dataset 100 frame)
    imgsz=640,                 # Resolusi gambar standar YOLO
    batch=8,                   # Jumlah gambar yang diproses per iterasi
    project='outputs',         # Folder utama penyimpanan hasil
    name='mining_model_v01'    # Nama folder eksperimen training pertama ini
)

print("\nTraining selesai! Model terbaikmu tersimpan di: outputs/mining_model_v01/weights/best.pt")