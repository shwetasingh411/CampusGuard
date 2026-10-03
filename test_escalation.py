from datetime import datetime, timedelta
from backend.alert_manager import check_escalation, create_alert


def main():
    event = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "event_type": "Restricted Zone Activity", "severity": "High"}
    alert = create_alert(event)
    print("Initial authority:", alert["authority"])
    alert["created_at"] = datetime.now() - timedelta(seconds=30)
    print("Before timeout (expected False):", check_escalation(alert, 60))
    alert["created_at"] = datetime.now() - timedelta(seconds=61)
    print("First escalation (expected True):", check_escalation(alert, 60))
    print("Authority (expected Admin/Coordinator):", alert["authority"])
    print("Immediate second escalation (expected False):", check_escalation(alert, 60))
    alert["escalated_at"] = (datetime.now() - timedelta(seconds=61)).isoformat(timespec="seconds")
    print("Second escalation (expected True):", check_escalation(alert, 60))
    print("Authority (expected Director):", alert["authority"])
    print("Escalation level (expected 2):", alert["escalation_level"])


if __name__ == "__main__":
    main()
