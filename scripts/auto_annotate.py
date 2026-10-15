import os
import shutil
from ultralytics import YOLO

MODEL_PATH = 'runs/detect/outputs/mining_model_v01-4/weights/best.pt'
FRAMES_DIR = 'frames'
MANUAL_DIR = 'cvat_raw'
CVAT_ZIP_DIR = 'outputs/cvat_upload_folder'
OBJ_TRAIN_DIR = os.path.join(CVAT_ZIP_DIR, 'obj_train_data')

print("Mulai proses Auto-Labeling oleh AI...")
model = YOLO(MODEL_PATH)

# 1. Jalankan AI dan simpan responnya di variabel 'results'
results = model.predict(
    source=FRAMES_DIR,
    save_txt=True,       
    conf=0.15,
    project='outputs/auto_annotate',
    name='predict_results',
    exist_ok=True
)

# 2. AMBIL ALAMAT PASTI DARI MESIN YOLO (Anti meleset)
ai_save_dir = results[0].save_dir
ai_labels_dir = os.path.join(ai_save_dir, 'labels')
print(f"\n=> AI menyimpan labelnya di: {ai_labels_dir}")

# 3. Bersihkan dan siapkan ulang folder ZIP CVAT
if os.path.exists(CVAT_ZIP_DIR):
    shutil.rmtree(CVAT_ZIP_DIR)
os.makedirs(OBJ_TRAIN_DIR, exist_ok=True)

# 4. Kumpulkan semua tebakan AI (Sekarang dijamin ketemu)
ai_count = 0
if os.path.exists(ai_labels_dir):
    for txt_file in os.listdir(ai_labels_dir):
        if txt_file.endswith('.txt'):
            shutil.copy(os.path.join(ai_labels_dir, txt_file), os.path.join(OBJ_TRAIN_DIR, txt_file))
            ai_count += 1
print(f"=> Berhasil mengambil {ai_count} tebakan dari AI.")

# 5. TIMPA dengan LABEL MANUAL aslimu
manual_count = 0
if os.path.exists(MANUAL_DIR):
    for txt_file in os.listdir(MANUAL_DIR):
        if txt_file.endswith('.txt') and txt_file not in ['classes.txt', 'obj.names']:
            if os.path.getsize(os.path.join(MANUAL_DIR, txt_file)) > 0:
                shutil.copy(os.path.join(MANUAL_DIR, txt_file), os.path.join(OBJ_TRAIN_DIR, txt_file))
                manual_count += 1
print(f"=> Berhasil mengamankan {manual_count} label manual.")

# 6. Buat file .txt kosong HANYA untuk sisa frame yang benar-benar kosong
empty_count = 0
if os.path.exists(FRAMES_DIR):
    for img_file in os.listdir(FRAMES_DIR):
        base_name = os.path.splitext(img_file)[0]
        txt_path = os.path.join(OBJ_TRAIN_DIR, base_name + '.txt')
        if not os.path.exists(txt_path):
            open(txt_path, 'a').close()
            empty_count += 1
print(f"=> Membuat {empty_count} label kosong untuk frame tanpa deteksi.")

# 7. Konfigurasi akhir CVAT
obj_names_content = """dump_truck\nexcavator\nbulldozer\nwheel_loader\nmotor_grader\ncar\ntruck"""
with open(os.path.join(CVAT_ZIP_DIR, 'obj.names'), 'w') as f:
    f.write(obj_names_content)

train_txt_content = ""
label_files = [f for f in os.listdir(OBJ_TRAIN_DIR) if f.endswith('.txt')]
label_files.sort()
for txt_file in label_files:
    train_txt_content += f"obj_train_data/{os.path.splitext(txt_file)[0]}.jpg\n"
with open(os.path.join(CVAT_ZIP_DIR, 'train.txt'), 'w') as f:
    f.write(train_txt_content)

with open(os.path.join(CVAT_ZIP_DIR, 'valid.txt'), 'w') as f:
    pass

with open(os.path.join(CVAT_ZIP_DIR, 'obj.data'), 'w') as f:
    f.write("classes = 7\nnames = obj.names\ntrain = train.txt\nvalid = valid.txt\nbackup = backup/")

# 8. Bungkus ulang menjadi file ZIP
shutil.make_archive('cvat_auto_labels', 'zip', CVAT_ZIP_DIR)
print("\nSelesai! File 'cvat_auto_labels.zip' siap diunggah ke CVAT.")