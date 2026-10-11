import unittest

from text_utils import excerpt, word_count


class TextUtils(unittest.TestCase):
    def test_word_count(self):
        self.assertEqual(word_count("one two  three"), 3)

    def test_excerpt(self):
        self.assertEqual(excerpt("a b c", words=2), "a b…")


if __name__ == "__main__":
    unittest.main()
