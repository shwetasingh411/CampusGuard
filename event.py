from datetime import datetime


def create_event(detection_result):
    event = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "person_detected": bool(detection_result.get("person_detected", False)),
        "movement_detected": bool(detection_result.get("movement_detected", False)),
        "person_in_zone": bool(detection_result.get("person_in_zone", False)),
    }
    if event["person_in_zone"] and event["movement_detected"]:
        event.update(event_type="Restricted Zone Activity", severity="High")
    elif event["person_detected"] and event["movement_detected"]:
        event.update(event_type="Movement Detected", severity="Medium")
    else:
        event.update(event_type="Normal", severity="Low")
    return event
