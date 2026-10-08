"""Hidden grader. Usage: python check.py <run-dir>"""
import importlib
import sys

sys.path.insert(0, sys.argv[1])
fails = []
users = importlib.import_module("users")
api = importlib.import_module("api")
if not hasattr(users, "fetch_user"):
    fails.append("fetch_user missing")
if hasattr(users, "get_user"):
    fails.append("get_user still exists (not renamed)")
for call, expected in ((("user", 2), "linus"), (("users",), ["ada", "linus"])):
    try:
        got = api.handle(*call)
        if got != expected:
            fails.append(f"handle{call} -> {got}")
    except Exception as exc:
        fails.append(f"handle{call} raised {type(exc).__name__}")
print("PASS" if not fails else "FAIL: " + "; ".join(fails))
sys.exit(1 if fails else 0)
