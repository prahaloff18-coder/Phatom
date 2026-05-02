from ultralytics import YOLO
import cv2
import time

# -----------------------------
# LOAD MODEL
# -----------------------------
model = YOLO("yolov8n.pt").to("cuda")

# -----------------------------
# VIDEO INPUT
# -----------------------------
cap = cv2.VideoCapture("test_video.mp4")

# -----------------------------
# MEMORY
# -----------------------------
prev_positions = {}
idle_start_time = {}
position_history = {}

frame_count = 0

cv2.namedWindow("Tracking", cv2.WINDOW_NORMAL)

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 360))

    # frame skip
    frame_count += 1
    if frame_count % 4 != 0:
        continue

    # -----------------------------
    # TRACKING
    # -----------------------------
    results = model.track(
        frame,
        persist=True,
        conf=0.5,
        imgsz=416,
        classes=[2, 3, 5, 7],
        verbose=False
)

    annotated_frame = frame.copy()
    boxes = results[0].boxes

    if boxes is not None and boxes.id is not None:
        ids = boxes.id.cpu().numpy()
        coords = boxes.xyxy.cpu().numpy()

        for box, track_id in zip(coords, ids):
            x1, y1, x2, y2 = map(int, box)

            center_y = int((y1 + y2) / 2)
            current_time = time.time()

            suspicious = None

            # -----------------------------
            # 🚨 IDLE DETECTION (FINAL)
            # -----------------------------
            if track_id not in position_history:
                position_history[track_id] = []

            position_history[track_id].append(center_y)

            if len(position_history[track_id]) > 20:
                position_history[track_id].pop(0)

            if len(position_history[track_id]) >= 15:

                max_pos = max(position_history[track_id])
                min_pos = min(position_history[track_id])
                movement_range = max_pos - min_pos

                # DEBUG
                cv2.putText(
                    annotated_frame,
                    f"range:{int(movement_range)}",
                    (x1, y2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255,255,0),
                    2
                )

                if movement_range < 40:
                    if track_id not in idle_start_time:
                        idle_start_time[track_id] = current_time

                    idle_duration = current_time - idle_start_time[track_id]
                    suspicious = f"Idle {idle_duration:.1f}s"
                else:
                    idle_start_time.pop(track_id, None)

            # -----------------------------
            # DRAW
            # -----------------------------
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0,255,0), 2)

            cv2.putText(
                annotated_frame,
                f"ID {int(track_id)}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,255,0),
                2
            )

            if suspicious:
                cv2.putText(
                    annotated_frame,
                    suspicious,
                    (x1, y1 - 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0,0,255),
                    2
                )

    cv2.imshow("Tracking", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -----------------------------
# CLEANUP
# -----------------------------
cap.release()
cv2.destroyAllWindows()