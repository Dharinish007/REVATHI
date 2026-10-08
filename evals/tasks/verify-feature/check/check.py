"""Hidden grader. Usage: python check.py <run-dir>"""
import sys

sys.path.insert(0, sys.argv[1])
from stats import median  # noqa: E402

fails = []
if median([3, 1, 2]) != 2:
    fails.append("odd/unsorted")
if median([4, 1, 3, 2]) != 2.5:
    fails.append("even")
data = [3, 1, 2]
median(data)
if data != [3, 1, 2]:
    fails.append("mutates input")
try:
    median([])
    fails.append("empty did not raise")
except ValueError:
    pass
print("PASS" if not fails else "FAIL: " + ", ".join(fails))
sys.exit(1 if fails else 0)
