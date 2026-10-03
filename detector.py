import cv2
from ultralytics import YOLO


class CampusGuardDetector:
    def __init__(self, model_path="yolo11n.pt", confidence_threshold=0.5, movement_threshold=5000):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.movement_threshold = movement_threshold
        self.previous_frame = None
        self.zone_x1, self.zone_y1, self.zone_x2, self.zone_y2 = 150, 100, 500, 400

    def detect(self, frame):
        if frame is None or frame.size == 0:
            raise ValueError("detect() received an empty frame")
        height, width = frame.shape[:2]
        x1, y1 = max(0, min(self.zone_x1, width - 1)), max(0, min(self.zone_y1, height - 1))
        x2, y2 = max(0, min(self.zone_x2, width - 1)), max(0, min(self.zone_y2, height - 1))
        person_detected = False
        person_in_zone = False
        results = self.model(frame, verbose=False)
        for result in results:
            for box in result.boxes:
                if int(box.cls[0]) != 0 or float(box.conf[0]) < self.confidence_threshold:
                    continue
                person_detected = True
                px1, py1, px2, py2 = map(int, box.xyxy[0])
                cx, cy = (px1 + px2) // 2, (py1 + py2) // 2
                if x1 <= cx <= x2 and y1 <= cy <= y2:
                    person_in_zone = True
                cv2.rectangle(frame, (px1, py1), (px2, py2), (255, 0, 0), 2)
                cv2.putText(frame, f"Person {float(box.conf[0]):.2f}", (px1, max(20, py1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        movement_detected = False
        if self.previous_frame is not None and self.previous_frame.shape == gray.shape:
            difference = cv2.absdiff(self.previous_frame, gray)
            _, threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)
            movement_detected = cv2.countNonZero(threshold) > self.movement_threshold
        self.previous_frame = gray
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, "RESTRICTED ZONE", (x1, max(20, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        return {"person_detected": person_detected, "person_in_zone": person_in_zone, "movement_detected": movement_detected, "frame": frame}
