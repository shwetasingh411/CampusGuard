import time
import cv2

from backend.alert_manager import acknowledge_alert, check_escalation, create_alert, resolve_alert
from backend.detector import CampusGuardDetector
from backend.event import create_event
from logger import log_alert, update_alert_log

CAMERA_INDEX = 0
COOLDOWN_SECONDS = 10
ESCALATION_TIMEOUT_SECONDS = 60
ACKNOWLEDGED_BY = "Security Operator"  # Change this to the operator's name if needed.


def latest_alert(alerts, statuses):
    return next((item for item in reversed(alerts) if item["status"] in statuses), None)


def main():
    detector = CampusGuardDetector()
    cap = cv2.VideoCapture(CAMERA_INDEX)
    last_alert_time = 0.0
    alerts = []
    try:
        if not cap.isOpened():
            print("Error: Camera could not be opened. Check camera permissions or CAMERA_INDEX.")
            return
        print("CampusGuard running | A: acknowledge | R: resolve | Q: quit")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read from camera.")
                break
            result = detector.detect(frame)
            now = time.monotonic()
            activity_detected = result["person_in_zone"] and result["movement_detected"]
            if activity_detected and now - last_alert_time >= COOLDOWN_SECONDS:
                event = create_event(result)
                alert = create_alert(event)
                alerts.append(alert)
                log_alert(alert)
                print(f"\nALERT {alert['alert_id']} | {alert['severity']} | assigned: {alert['authority']} | {alert['status']}")
                last_alert_time = now
            for alert in alerts:
                if check_escalation(alert, ESCALATION_TIMEOUT_SECONDS):
                    update_alert_log(alert)
                    print(f"ESCALATED {alert['alert_id']} -> {alert['authority']} (level {alert['escalation_level']})")
            label = "ACTIVITY DETECTED" if activity_detected else "Monitoring..."
            color = (0, 0, 255) if activity_detected else (0, 255, 0)
            cv2.putText(frame, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cv2.putText(frame, "A: acknowledge | R: resolve | Q: quit", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
            cv2.imshow("CampusGuard AI Detector", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("a"):
                alert = latest_alert(alerts, {"Pending"})
                if alert and acknowledge_alert(alert, ACKNOWLEDGED_BY):
                    update_alert_log(alert)
                    print(f"Acknowledged {alert['alert_id']} by {ACKNOWLEDGED_BY}")
                else:
                    print("No pending alert to acknowledge.")
            elif key == ord("r"):
                alert = latest_alert(alerts, {"Pending", "Acknowledged"})
                if alert and resolve_alert(alert):
                    update_alert_log(alert)
                    print(f"Resolved {alert['alert_id']}")
                else:
                    print("No active alert to resolve.")
            elif key == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
