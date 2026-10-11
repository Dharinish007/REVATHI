import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.dates import parse_date  # noqa: E402


class Dates(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(parse_date("2026-10-11"), date(2026, 10, 11))

    def test_spaces(self):
        self.assertEqual(parse_date(" 2026-01-02 "), date(2026, 1, 2))


if __name__ == "__main__":
    unittest.main()
