"""Run with: python -m unittest enhancements.test_booking_store"""

import json
import os
import tempfile
import unittest

from .booking_store import (
    list_bookings,
    new_booking_id,
    save_booking,
)


class BookingStoreTests(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(
            self._tmp_dir.name, "sub", "bookings.jsonl"
        )

    def tearDown(self):
        self._tmp_dir.cleanup()

    def test_save_creates_parent_dirs_and_id(self):
        booking = {
            "date": "2026-09-25",
            "time": "10:00 AM",
            "service": "Ceramic Coating",
        }

        stored = save_booking(booking, path=self.path)

        self.assertTrue(os.path.exists(self.path))
        self.assertTrue(stored["id"].startswith("FT-"))
        self.assertIn("created_at", stored)

        with open(self.path, "r", encoding="utf-8") as handle:
            lines = [line for line in handle if line.strip()]

        self.assertEqual(len(lines), 1)
        self.assertEqual(json.loads(lines[0])["id"], stored["id"])

    def test_append_keeps_prior_records(self):
        save_booking({"service": "A"}, path=self.path)
        save_booking({"service": "B"}, path=self.path)

        records = list_bookings(path=self.path)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["service"], "A")
        self.assertEqual(records[1]["service"], "B")

    def test_id_format(self):
        self.assertRegex(new_booking_id(), r"^FT-\d{8}-[0-9A-F]{6}$")

    def test_list_with_date_filter(self):
        save_booking({"date": "2026-09-25"}, path=self.path)
        save_booking({"date": "2026-09-26"}, path=self.path)

        filtered = list_bookings(date="2026-09-25", path=self.path)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["date"], "2026-09-25")

    def test_missing_file_returns_empty(self):
        self.assertEqual(list_bookings(path=self.path), [])

    def test_corrupt_line_is_skipped(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("{not valid json}\n")
            handle.write(json.dumps({"service": "ok"}) + "\n")

        records = list_bookings(path=self.path)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["service"], "ok")


if __name__ == "__main__":
    unittest.main()