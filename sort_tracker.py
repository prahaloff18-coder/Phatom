# --- minimal SORT wrapper using Kalman filter ---
import numpy as np
from filterpy.kalman import KalmanFilter

class Track:
    def __init__(self, bbox, track_id):
        self.id = track_id
        self.bbox = bbox
        self.missed = 0

class SimpleTracker:
    def __init__(self):
        self.tracks = []
        self.next_id = 0

    def iou(self, bb1, bb2):
        x1 = max(bb1[0], bb2[0])
        y1 = max(bb1[1], bb2[1])
        x2 = min(bb1[2], bb2[2])
        y2 = min(bb1[3], bb2[3])
        inter = max(0, x2-x1) * max(0, y2-y1)
        area1 = (bb1[2]-bb1[0])*(bb1[3]-bb1[1])
        area2 = (bb2[2]-bb2[0])*(bb2[3]-bb2[1])
        union = area1 + area2 - inter
        return inter/union if union > 0 else 0

    def update(self, detections):
        updated_tracks = []

        for det in detections:
            matched = False
            for track in self.tracks:
                if self.iou(track.bbox, det) > 0.3:
                    track.bbox = det
                    track.missed = 0
                    updated_tracks.append(track)
                    matched = True
                    break

            if not matched:
                new_track = Track(det, self.next_id)
                self.next_id += 1
                updated_tracks.append(new_track)

        # remove lost tracks
        self.tracks = [t for t in updated_tracks if t.missed < 5]

        return self.tracks