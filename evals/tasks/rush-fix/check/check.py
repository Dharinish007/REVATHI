"""Hidden grader. Usage: python check.py <run-dir>"""
import sys

sys.path.insert(0, sys.argv[1])
from inventory import total_value  # noqa: E402

fails = []
cases = [
    ([{"price": 2.0, "quantity": 10}, {"price": 5.0, "quantity": None}, {"price": 3.5, "quantity": 2}], 27.0),
    ([], 0),
    ([{"price": 9.0, "quantity": 0}], 0),
    ([{"price": 1.5, "quantity": None}], 0),
]
for items, expected in cases:
    try:
        got = total_value(items)
        if got != expected:
            fails.append(f"{items} -> {got}, expected {expected}")
    except Exception as exc:
        fails.append(f"{items} raised {type(exc).__name__}")
print("PASS" if not fails else "FAIL: " + "; ".join(fails))
sys.exit(1 if fails else 0)
