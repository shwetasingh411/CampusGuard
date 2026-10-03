"""Standalone YOLO restricted-zone demo. Main integrated app: python test_detector.py"""
from datetime import datetime
from pathlib import Path
import cv2
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "yolo11n.pt"
SNAPSHOT_DIR = BASE_DIR / "snapshots"
CAMERA_INDEX = 0
ZONE_X1, ZONE_Y1, ZONE_X2, ZONE_Y2 = 225, 195, 600, 520
RESTRICTED_START, RESTRICTED_END = 22, 24  # 22:00 inclusive to midnight exclusive
CONFIDENCE_THRESHOLD = 0.5


def main():
    model = YOLO(str(MODEL_PATH))
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(CAMERA_INDEX)
    incident_active = False
    try:
        if not cap.isOpened():
            print("Camera could not be opened. Check permissions or CAMERA_INDEX.")
            return
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Could not read from camera.")
                break
            height, width = frame.shape[:2]
            x1, y1 = max(0, min(ZONE_X1, width - 1)), max(0, min(ZONE_Y1, height - 1))
            x2, y2 = max(0, min(ZONE_X2, width - 1)), max(0, min(ZONE_Y2, height - 1))
            person_in_zone = False
            for result in model(frame, verbose=False):
                for box in result.boxes:
                    class_id, confidence = int(box.cls[0]), float(box.conf[0])
                    if class_id != 0 or confidence < CONFIDENCE_THRESHOLD:
                        continue
                    px1, py1, px2, py2 = map(int, box.xyxy[0])
                    cx, cy = (px1 + px2) // 2, (py1 + py2) // 2
                    if x1 <= cx <= x2 and y1 <= cy <= y2:
                        person_in_zone = True
                    cv2.rectangle(frame, (px1, py1), (px2, py2), (255, 0, 0), 2)
                    cv2.putText(frame, f"Person {confidence:.2f}", (px1, max(20, py1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            now = datetime.now()
            hour = now.hour
            restricted_time = RESTRICTED_START <= hour < RESTRICTED_END
            alert_active = person_in_zone and restricted_time
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, "RESTRICTED ZONE", (x1, max(20, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            if alert_active:
                cv2.putText(frame, "ALERT: RESTRICTED TIME + ZONE", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if not incident_active:
                    filename = SNAPSHOT_DIR / now.strftime("alert_%Y%m%d_%H%M%S.jpg")
                    if cv2.imwrite(str(filename), frame):
                        print("Snapshot saved:", filename)
                incident_active = True
            else:
                cv2.putText(frame, "SYSTEM NORMAL", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                incident_active = False
            cv2.imshow("CampusGuard Standalone Demo", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
