import unittest

from pager import page_count


class PagerTest(unittest.TestCase):
    def test_page_count(self):
        self.assertEqual(page_count(list(range(35))), 4)


if __name__ == "__main__":
    unittest.main()
