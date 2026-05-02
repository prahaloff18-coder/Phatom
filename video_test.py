from ultralytics import YOLO
import cv2
import time
from deep_sort_realtime.deepsort_tracker import DeepSort

# ---------------------------
# MODEL + TRACKER
# ---------------------------
model=YOLO("yolov8m.pt")   # use yolov8s.pt if slow

tracker = DeepSort(
    max_age=60,
    n_init=3,
    max_cosine_distance=0.3,
    nn_budget=100
)

# ---------------------------
# VIDEO
# ---------------------------
cap = cv2.VideoCapture("test_video.mp4")

# ---------------------------
# COUNTING + TRACK MEMORY
# ---------------------------
line_y = 400
vehicle_count = 0
counted_ids = set()

track_history = {}
prev_positions = {}
prev_time = {}

# ---------------------------
# MAIN LOOP
# ---------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize for better detection
    frame = cv2.resize(frame, (1280, 720))

    # ---------------------------
    # DETECTION
    # ---------------------------
    results = model(frame, conf=0.4)[0]

    detections = []

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        conf = float(box.conf[0])
        cls = int(box.cls[0])

        # Only vehicles
        if cls in [2, 3, 5, 7]:
            detections.append(([x1, y1, x2 - x1, y2 - y1], conf, 'vehicle'))

    # ---------------------------
    # TRACKING
    # ---------------------------
    tracks = tracker.update_tracks(detections, frame=frame)

    current_time = time.time()

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        l, t, w, h = map(int, track.to_ltrb())

        center_y = int((t + (t + h)) / 2)

        # ---------------------------
        # COUNTING
        # ---------------------------
        if center_y > line_y:
            if track_id not in counted_ids:
                vehicle_count += 1
                counted_ids.add(track_id)

        # ---------------------------
        # DIRECTION
        # ---------------------------
        if track_id not in track_history:
            track_history[track_id] = []

        track_history[track_id].append(center_y)

        direction = ""
        if len(track_history[track_id]) > 5:
            if track_history[track_id][-1] > track_history[track_id][0]:
                direction = "Down"
            else:
                direction = "Up"

        # ---------------------------
        # SPEED ESTIMATION
        # ---------------------------
        speed_text = ""

        if track_id in prev_positions:
            dy = abs(center_y - prev_positions[track_id])
            dt = current_time - prev_time[track_id]

            if dt > 0:
                speed = dy / dt
                speed_text = f"{int(speed)} px/s"

        prev_positions[track_id] = center_y
        prev_time[track_id] = current_time

        # ---------------------------
        # DRAW
        # ---------------------------
        cv2.rectangle(frame, (l, t), (l + w, t + h), (0, 255, 0), 2)

        cv2.putText(frame, f"ID {track_id}",
                    (l, t - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 2)

        if direction:
            cv2.putText(frame, direction,
                        (l, t - 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 0), 2)

        if speed_text:
            cv2.putText(frame, speed_text,
                        (l, t - 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 255), 2)

    # ---------------------------
    # DRAW COUNT LINE
    # ---------------------------
    cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (0, 0, 255), 2)

    cv2.putText(frame, f"Count: {vehicle_count}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2)

    # ---------------------------
    # DISPLAY
    # ---------------------------
    cv2.imshow("Traffic System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------------------
# CLEANUP
# ---------------------------
cap.release()
cv2.destroyAllWindows()
print("Loading NEW VIDEO...")
print("VIDEO PATH:", "test_video.mp4")

