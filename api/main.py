import cv2
import time
import math
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "runs/detect/outputs/mining_model_v01-5/weights/best.pt"
model = YOLO(MODEL_PATH)
VIDEO_PATH = "videos/mining_01_lite.mp4"

stats_data = {
    "dump_truck": 0,
    "excavator": 0,
    "bulldozer": 0,
    "car": 0,
    "motor_grader": 0,
    "latency_ms": 0,
    "model_version": "v0.2 (Trained)",
    "logs": []
}

id_mapping = {}

# MEMORI ANTI-DUPLIKAT: Menyimpan riwayat objek terakhir per kelas
# Format: { "motor_grader": [{"local_id": 1, "cx": 400, "cy": 300, "last_seen": 1700000.0}] }
recent_objects = {
    "dump_truck": [],
    "excavator": [],
    "bulldozer": [],
    "car": [],
    "motor_grader": []
}

class_colors = {
    "dump_truck": (0, 165, 255),
    "excavator": (0, 255, 0),
    "bulldozer": (255, 0, 0),
    "car": (255, 0, 255),
    "motor_grader": (255, 255, 0)
}

def generate_frames():
    cap = cv2.VideoCapture(VIDEO_PATH)
    frame_count = 0
    
    while True:
        success, frame = cap.read()
        
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            stats_data["dump_truck"] = 0
            stats_data["excavator"] = 0
            stats_data["bulldozer"] = 0
            stats_data["car"] = 0
            stats_data["motor_grader"] = 0
            stats_data["logs"].clear()
            id_mapping.clear()
            for k in recent_objects:
                recent_objects[k].clear()
            continue
            
        frame_count += 1
        if frame_count % 3 != 0:
            continue
            
        frame = cv2.resize(frame, (960, 540))
        start_time = time.time()
            
        # 1. Turunkan conf ke 0.25 agar deteksi Motor Grader tidak mudah putus
        results = model.track(frame, persist=True, conf=0.25, iou=0.5, verbose=False, imgsz=320)
        annotated_frame = frame.copy()
        
        boxes = results[0].boxes
        now = time.time()
        
        if boxes is not None and boxes.id is not None:
            class_ids = boxes.cls.int().cpu().tolist()
            track_ids = boxes.id.int().cpu().tolist()
            confs = boxes.conf.cpu().tolist()
            xyxys = boxes.xyxy.cpu().tolist()
            
            for class_id, track_id, conf, xyxy in zip(class_ids, track_ids, confs, xyxys):
                class_name = model.names[class_id]
                safe_class_name = class_name.replace(" ", "_")
                
                if safe_class_name in stats_data:
                    x1, y1, x2, y2 = map(int, xyxy)
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    
                    # JIKA MUNCUL TRACK_ID BARU DARI YOLO...
                    if track_id not in id_mapping:
                        matched_local_id = None
                        
                        # 2. CEK APAKAH INI KENDARAAN YANG SAMA YANG BARU SAJA PUTUS DETEKSINYA
                        for obj in recent_objects[safe_class_name]:
                            dist = math.hypot(cx - obj["cx"], cy - obj["cy"])
                            time_diff = now - obj["last_seen"]
                            
                            # Jika hilang kurang dari 4 detik dan posisinya masih berdekatan (< 220 piksel)
                            if time_diff < 4.0 and dist < 220:
                                matched_local_id = obj["local_id"]
                                obj["cx"] = cx
                                obj["cy"] = cy
                                obj["last_seen"] = now
                                break
                        
                        if matched_local_id is not None:
                            # Gunakan kembali ID lama tanpa menambah counter statistik!
                            id_mapping[track_id] = matched_local_id
                        else:
                            # Benar-benar kendaraan baru! Tambahkan ke statistik
                            stats_data[safe_class_name] += 1
                            new_local_id = stats_data[safe_class_name]
                            id_mapping[track_id] = new_local_id
                            
                            recent_objects[safe_class_name].append({
                                "local_id": new_local_id,
                                "cx": cx,
                                "cy": cy,
                                "last_seen": now
                            })
                            
                            current_time = datetime.now().strftime("%H:%M:%S")
                            display_name = class_name.replace("_", " ").title()
                            log_msg = f"[{current_time}] {display_name} #{new_local_id} terdeteksi (Conf: {int(conf * 100)}%)"
                            
                            stats_data["logs"].insert(0, log_msg)
                            if len(stats_data["logs"]) > 15:
                                stats_data["logs"].pop()
                    else:
                        # Jika ID sudah terdaftar, perbarui terus posisi dan waktu terakhir terlihatnya
                        current_local_id = id_mapping[track_id]
                        for obj in recent_objects[safe_class_name]:
                            if obj["local_id"] == current_local_id:
                                obj["cx"] = cx
                                obj["cy"] = cy
                                obj["last_seen"] = now
                                break
                    
                    local_id = id_mapping[track_id]
                    color = class_colors.get(safe_class_name, (0, 255, 0))
                    
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    label = f"{safe_class_name} #{local_id} {conf:.2f}"
                    
                    (t_w, t_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(annotated_frame, (x1, y1 - 24), (x1 + t_w + 4, y1), color, -1)
                    cv2.putText(annotated_frame, label, (x1 + 2, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        end_time = time.time()
        stats_data["latency_ms"] = int((end_time - start_time) * 1000)

        ret, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/")
def home():
    return {"message": "Server AI Mining Vehicle Aktif!"}

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/stats")
def get_stats():
    return stats_data

@app.post("/reset")
def reset_stats():
    stats_data["dump_truck"] = 0
    stats_data["excavator"] = 0
    stats_data["bulldozer"] = 0
    stats_data["car"] = 0
    stats_data["motor_grader"] = 0
    stats_data["logs"].clear()
    id_mapping.clear()
    for k in recent_objects:
        recent_objects[k].clear()
    return {"status": "success", "message": "Memori AI direset!"}