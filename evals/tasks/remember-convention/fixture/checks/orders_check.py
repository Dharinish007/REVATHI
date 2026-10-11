import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orders import add_tax, subtotal  # noqa: E402


class Orders(unittest.TestCase):
    def test_subtotal(self):
        self.assertEqual(subtotal([{"price_cents": 250, "qty": 2}, {"price_cents": 99, "qty": 1}]), 599)

    def test_tax_rounds_half_up(self):
        self.assertEqual(add_tax(1001, 50), 1502)  # 1501.5 -> 1502

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            add_tax(100, -1)


if __name__ == "__main__":
    unittest.main()
