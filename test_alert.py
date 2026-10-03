from backend.alert_manager import acknowledge_alert, create_alert, resolve_alert


def main():
    event = {"timestamp": "2026-10-03 18:30:00", "event_type": "Restricted Zone Activity", "severity": "High"}
    alert = create_alert(event)
    print("Before:", alert["status"])
    print("Acknowledgement successful:", acknowledge_alert(alert, "Security Officer"))
    print("After:", alert["status"])
    print("Acknowledged by:", alert["acknowledged_by"])
    print("Resolution successful:", resolve_alert(alert))
    print("Final status:", alert["status"])


if __name__ == "__main__":
    main()
