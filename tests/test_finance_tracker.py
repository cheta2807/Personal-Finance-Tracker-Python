import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import finance_tracker


class AmountValidationTests(unittest.TestCase):
    def test_accepts_valid_amounts(self):
        self.assertEqual(finance_tracker.parse_amount("1250"), Decimal("1250"))
        self.assertEqual(finance_tracker.parse_amount("1,250.50"), Decimal("1250.50"))

    def test_rejects_invalid_amounts(self):
        for value in ("", "abc", "0", "-3", "1.234", "NaN", "Infinity"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    finance_tracker.parse_amount(value)


class DateValidationTests(unittest.TestCase):
    def test_accepts_and_normalizes_iso_date(self):
        self.assertEqual(finance_tracker.parse_date("2026-09-10"), "2026-09-10")

    def test_rejects_invalid_calendar_date(self):
        for value in ("2026-02-30", "10-09-2026", "not a date"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    finance_tracker.parse_date(value)

    def test_empty_date_defaults_to_today(self):
        self.assertEqual(finance_tracker.parse_date("  "), date.today().isoformat())


class StorageTests(unittest.TestCase):
    def test_save_and_load_round_trip(self):
        transactions = [
            {
                "type": "expense",
                "amount": 12.5,
                "category": "Food",
                "description": "Lunch",
                "date": "2026-09-10",
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "finance_data.json"
            with patch.object(finance_tracker, "DATA_FILE", data_file):
                finance_tracker.save_transactions(transactions)
                self.assertEqual(finance_tracker.load_transactions(), transactions)


if __name__ == "__main__":
    unittest.main()
