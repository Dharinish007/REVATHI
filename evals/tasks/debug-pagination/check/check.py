"""Hidden grader. Usage: python check.py <run-dir>"""
import sys

sys.path.insert(0, sys.argv[1])
from pager import all_pages, paginate  # noqa: E402

items = list(range(35))
pages = all_pages(items)
ok = (
    len(pages) == 4
    and pages[0] == list(range(10))
    and pages[3] == list(range(30, 35))
    and paginate(items, 1) == list(range(10))
)
print("PASS" if ok else f"FAIL: {pages}")
sys.exit(0 if ok else 1)
