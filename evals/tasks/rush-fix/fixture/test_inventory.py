import unittest

from inventory import total_value

ITEMS = [
    {"name": "pen", "price": 2.0, "quantity": 10},
    {"name": "ink", "price": 5.0, "quantity": None},  # discontinued
    {"name": "pad", "price": 3.5, "quantity": 2},
]


class TotalValueTest(unittest.TestCase):
    def test_total_value(self):
        self.assertEqual(total_value(ITEMS), 27.0)


if __name__ == "__main__":
    unittest.main()
