import cv2
import time
import requests
from ultralytics import YOLO

# ---------------- LOAD MODEL ----------------
model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture("test_video.mp4")

# ---------------- CONTROL ----------------
sent_vehicle_ids = set()
alert_sent_ids = set()

# ---------------- API FUNCTIONS ----------------
def send_vehicle(vehicle_id, bbox):
    url = "http://127.0.0.1:8000/add-vehicle"
    data = {
        "vehicle_id": vehicle_id,
        "type": "car",
        "frame": int(time.time()),
        "bbox": bbox
    }
    try:
        requests.post(url, json=data)
    except:
        pass


def send_alert(vehicle_id):
    url = "http://127.0.0.1:8000/alert"
    data = {
        "vehicle_id": vehicle_id,
        "type": "IDLE"
    }
    try:
        requests.post(url, json=data)
    except:
        pass


# ---------------- TRACK MEMORY ----------------
idle_time_map = {}
frame_count = 0

# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # 🔥 skip frames (speed)
    if frame_count % 2 != 0:
        continue

    frame = cv2.resize(frame, (416, 416))

    results = model.track(frame, persist=True, conf=0.5, classes=[2])
    current_time = time.time()

    for r in results:
        if r.boxes.id is None:
            continue

        for box, track_id in zip(r.boxes.xyxy, r.boxes.id):

            x1, y1, x2, y2 = map(int, box.tolist())
            track_id = int(track_id)

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # ---------------- SEND VEHICLE ----------------
            if track_id not in sent_vehicle_ids:
                send_vehicle(track_id, [x1, y1, x2, y2])
                sent_vehicle_ids.add(track_id)

            # ---------------- IDLE DETECTION ----------------
            if track_id not in idle_time_map:
                idle_time_map[track_id] = {
                    "positions": [],
                    "start": current_time,
                    "alerted": False
                }

            idle_time_map[track_id]["positions"].append((cx, cy))

            if len(idle_time_map[track_id]["positions"]) > 15:
                idle_time_map[track_id]["positions"].pop(0)

            positions = idle_time_map[track_id]["positions"]

            if len(positions) >= 10:
                total_movement = 0

                for i in range(1, len(positions)):
                    x1p, y1p = positions[i - 1]
                    x2p, y2p = positions[i]
                    total_movement += abs(x2p - x1p) + abs(y2p - y1p)

                avg_movement = total_movement / len(positions)

                # DEBUG movement
                cv2.putText(frame, f"mv:{int(avg_movement)}",
                            (x1, y2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 255, 0), 2)

                # STRICT IDLE CONDITION
                if avg_movement < 5 and len(positions) >= 12:
                    idle_duration = current_time - idle_time_map[track_id]["start"]

                    if idle_duration > 7:
                        cv2.putText(frame, f"Idle {idle_duration:.1f}s",
                                    (x1, y1 - 35),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.7, (0, 0, 255), 2)

                    if idle_duration > 10 and not idle_time_map[track_id]["alerted"]:
                        send_alert(track_id)
                        idle_time_map[track_id]["alerted"] = True

                else:
                    # reset if moving
                    idle_time_map[track_id]["start"] = current_time
                    idle_time_map[track_id]["alerted"] = False

            # ---------------- DRAW ----------------
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.putText(frame, f"ID {track_id}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

    cv2.imshow("FINAL DEMO", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()