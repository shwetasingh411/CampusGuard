"""Logger smoke test using a temporary CSV; leaves project logs unchanged."""
import os
import tempfile
from datetime import datetime, timedelta
import logger
from backend.alert_manager import check_escalation, create_alert, acknowledge_alert, resolve_alert


def main():
    original_path = logger.LOG_FILE
    with tempfile.TemporaryDirectory() as directory:
        logger.LOG_FILE = os.path.join(directory, "test_logs.csv")
        try:
            event = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "event_type": "Test Event", "severity": "High"}
            alert = create_alert(event)
            logger.log_alert(alert)
            alert["created_at"] = datetime.now() - timedelta(seconds=61)
            print("Escalated:", check_escalation(alert, 60))
            logger.update_alert_log(alert)
            print("Authority after escalation:", alert["authority"])
            print("Acknowledged:", acknowledge_alert(alert, "Test Operator"))
            logger.update_alert_log(alert)
            print("Resolved:", resolve_alert(alert))
            logger.update_alert_log(alert)
            print("Logger test complete; temporary file will be removed.")
        finally:
            logger.LOG_FILE = original_path


if __name__ == "__main__":
    main()
