import unittest

import api


class ApiTest(unittest.TestCase):
    def test_single_user(self):
        self.assertEqual(api.handle("user", 1), "ada")

    def test_all_users(self):
        self.assertEqual(api.handle("users"), ["ada", "linus"])


if __name__ == "__main__":
    unittest.main()
