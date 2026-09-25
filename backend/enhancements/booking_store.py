"""JSONL-backed storage for customer booking records.

Failure-safe: every write happens through fsync so a crash can never
leave a half-written line in the file. Paths stay overrideable for tests.
"""

import datetime
import json
import os
import threading
import uuid

from src import config

_LOCK = threading.Lock()

BOOKINGS_PATH = config.BOOKINGS_PATH


def _today_key(dt=None):
    dt = dt or datetime.datetime.now()
    return dt.strftime("%Y%m%d")


def new_booking_id(dt=None):
    dt = dt or datetime.datetime.now()
    sequence = uuid.uuid4().hex[:6].upper()
    return "FT-{}-{}".format(_today_key(dt), sequence)


def save_booking(booking, path=BOOKINGS_PATH):
    """Append one booking record to the JSONL file. Returns the stored
    record (with its generated id and created_at filled in)."""
    now = datetime.datetime.now()

    if not booking.get("id"):
        booking["id"] = new_booking_id(now)

    if not booking.get("created_at"):
        booking["created_at"] = now.isoformat(timespec="seconds")

    # Read-modify-write through a temp file + rename so a crash can
    # never leave a partial line in the real file.
    with _LOCK:
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        existing = ""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                existing = handle.read()

        staged = "{}.tmp".format(path)

        with open(staged, "w", encoding="utf-8") as handle:
            handle.write(existing)
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            handle.write(json.dumps(booking, ensure_ascii=False))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(staged, path)

        return dict(booking)


def list_bookings(date=None, path=BOOKINGS_PATH):
    """Read every record. If `date` is "YYYY-MM-DD" (or "YYYYMMDD"),
    keep only bookings whose date matches."""
    records = []

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if date is not None:
        date_key = date.replace("-", "")
        records = [
            record
            for record in records
            if record.get("date")
            and _today_key(_parse_dt(record["date"])) == date_key
        ]

    return records


def _parse_dt(value):
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d",
        "%Y%m%d",
    ):
        try:
            return datetime.datetime.strptime(value, fmt)
        except (TypeError, ValueError):
            continue
    return datetime.datetime.now()