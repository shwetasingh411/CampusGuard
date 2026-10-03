import csv
import os
import shutil
import tempfile
from datetime import datetime

LOG_FILE = "campusguard_logs.csv"
FIELDS = [
    "alert_id", "timestamp", "event_type", "severity", "authority", "status",
    "acknowledged_by", "acknowledged_at", "escalation_level", "created_at",
    "escalated_at", "resolved_at",
]


def format_value(value):
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return "" if value is None else value


def prepare_alert(alert):
    return {field: format_value(alert.get(field, "")) for field in FIELDS}


def _write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") or "" for field in FIELDS})


def ensure_log_file():
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        _write_rows(LOG_FILE, [])
        return
    with open(LOG_FILE, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        old_fields = reader.fieldnames or []
        rows = list(reader)
    if old_fields == FIELDS:
        return
    backup = LOG_FILE + ".bak"
    if not os.path.exists(backup):
        shutil.copy2(LOG_FILE, backup)
    fd, temp_path = tempfile.mkstemp(prefix="campusguard_", suffix=".csv", dir=os.path.dirname(os.path.abspath(LOG_FILE)))
    os.close(fd)
    try:
        _write_rows(temp_path, rows)
        os.replace(temp_path, LOG_FILE)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def log_alert(alert):
    ensure_log_file()
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writerow(prepare_alert(alert))


def update_alert_log(alert):
    ensure_log_file()
    with open(LOG_FILE, "r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    target_id = str(alert["alert_id"])
    updated = prepare_alert(alert)
    found = False
    for row in rows:
        if row.get("alert_id") == target_id:
            row.update(updated)
            found = True
            break
    if not found:
        log_alert(alert)
        return
    fd, temp_path = tempfile.mkstemp(prefix="campusguard_", suffix=".csv", dir=os.path.dirname(os.path.abspath(LOG_FILE)))
    os.close(fd)
    try:
        _write_rows(temp_path, rows)
        os.replace(temp_path, LOG_FILE)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
