import os
import shutil
import glob

# Pisahkan path sumber: txt dari cvat_raw, gambar dari frames
LABELS_DIR = 'cvat_raw'
IMAGES_DIR = 'frames'
DATASET_DIR = 'dataset'

# Hapus folder dataset lama agar bersih
if os.path.exists(DATASET_DIR):
    shutil.rmtree(DATASET_DIR)

for split in ['train', 'val', 'test']:
    os.makedirs(os.path.join(DATASET_DIR, 'images', split), exist_ok=True)
    os.makedirs(os.path.join(DATASET_DIR, 'labels', split), exist_ok=True)

# Kumpulkan file label
# Kumpulkan file label yang benar DAN ada isinya (mengabaikan frame kosong)
label_files = []
for f in os.listdir(LABELS_DIR):
    if f.endswith('.txt') and f not in ['classes.txt', 'obj.names']:
        txt_path = os.path.join(LABELS_DIR, f)
        # Hanya ambil file yang ukurannya lebih dari 0 byte (sudah dilabeli)
        if os.path.getsize(txt_path) > 0:
            label_files.append(f)

label_files.sort()

total_files = len(label_files)
train_count = int(total_files * 0.70)
val_count = int(total_files * 0.20)

print(f"Total frame berlabel: {total_files}")
copied_images = 0

for i, txt_file in enumerate(label_files):
    base_name = os.path.splitext(txt_file)[0]
    
    # Cari gambar aslinya di folder 'frames'
    img_search = glob.glob(os.path.join(IMAGES_DIR, f"{base_name}.*"))
    img_src = img_search[0] if img_search else None
    
    if img_src:
        if i < train_count:
            split = 'train'
        elif i < train_count + val_count:
            split = 'val'
        else:
            split = 'test'
            
        txt_src = os.path.join(LABELS_DIR, txt_file)
        img_ext = os.path.splitext(img_src)[1]
        img_dest = base_name + img_ext
        
        # Copy gambar dari frames/ dan label dari cvat_raw/
        shutil.copy(img_src, os.path.join(DATASET_DIR, 'images', split, img_dest))
        shutil.copy(txt_src, os.path.join(DATASET_DIR, 'labels', split, txt_file))
        copied_images += 1
    else:
        print(f"Peringatan: Tidak menemukan gambar {base_name} di folder '{IMAGES_DIR}'")

print(f"Berhasil menyalin {copied_images} gambar dan label ke struktur folder.")

# Buat file data.yaml
yaml_content = f"""path: {os.path.abspath(DATASET_DIR)}
train: images/train
val: images/val
test: images/test

nc: 7
names: 
  0: dump_truck
  1: excavator
  2: bulldozer
  3: wheel_loader
  4: motor_grader
  5: car
  6: label_7
"""

with open(os.path.join(DATASET_DIR, 'data.yaml'), 'w') as f:
    f.write(yaml_content)

print("Dataset siap!")