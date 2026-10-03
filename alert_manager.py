from datetime import datetime

HIERARCHY = {
    "Guard": "Supervisor",
    "Supervisor": "Security Officer",
    "Security Officer": "Admin/Coordinator",
    "Admin/Coordinator": "Director",
}


def create_alert(event):
    now = datetime.now()
    severity = event.get("severity", "Low")
    authority = {"High": "Security Officer", "Medium": "Supervisor"}.get(severity, "Guard")
    return {
        "alert_id": now.strftime("%Y%m%d%H%M%S%f"),
        "timestamp": event.get("timestamp", now.strftime("%Y-%m-%d %H:%M:%S")),
        "event_type": event.get("event_type", "Unknown Event"),
        "severity": severity,
        "authority": authority,
        "status": "Pending",
        "acknowledged_by": "",
        "acknowledged_at": "",
        "escalation_level": 0,
        "created_at": now,
        "escalated_at": "",
        "resolved_at": "",
    }


def acknowledge_alert(alert, person_name):
    if alert.get("status") != "Pending" or not isinstance(person_name, str) or not person_name.strip():
        return False
    alert["status"] = "Acknowledged"
    alert["acknowledged_by"] = person_name.strip()
    alert["acknowledged_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return True


def resolve_alert(alert):
    if alert.get("status") not in ("Pending", "Acknowledged"):
        return False
    alert["status"] = "Resolved"
    alert["resolved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return True


def check_escalation(alert, timeout_seconds=60):
    if alert.get("status") != "Pending":
        return False
    try:
        reference_time = alert.get("escalated_at") or alert["created_at"]
        if isinstance(reference_time, str):
            reference_time = datetime.fromisoformat(reference_time)
        elapsed = (datetime.now() - reference_time).total_seconds()
    except (KeyError, TypeError, ValueError):
        return False
    if elapsed < timeout_seconds:
        return False
    next_authority = HIERARCHY.get(alert.get("authority"))
    if next_authority is None:
        return False
    now = datetime.now()
    alert["authority"] = next_authority
    alert["escalation_level"] = int(alert.get("escalation_level", 0)) + 1
    alert["escalated_at"] = now.isoformat(timespec="seconds")
    return True
