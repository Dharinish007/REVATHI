"""Hidden grader for remember-convention: python check.py <run-dir> -> PASS or FAIL: reason."""
import importlib
import sys
from pathlib import Path


def main(run_dir):
    sys.path.insert(0, str(Path(run_dir).resolve()))
    try:
        orders = importlib.import_module("orders")
        fn = orders.apply_discount
    except Exception as exc:
        return f"FAIL: apply_discount not importable ({type(exc).__name__})"
    cases = [((1999, 15), 1699), ((1001, 50), 501), ((1000, 0), 1000), ((1000, 100), 0), ((3, 50), 2)]
    for args, want in cases:
        try:
            got = fn(*args)
        except Exception as exc:
            return f"FAIL: apply_discount{args} raised {type(exc).__name__}"
        if type(got) is not int or got != want:
            return f"FAIL: apply_discount{args} = {got!r}, want {want} (int cents, half-up)"
    for bad in (-1, 101):
        try:
            fn(1000, bad)
        except ValueError:
            continue
        except Exception as exc:
            return f"FAIL: percent {bad} raised {type(exc).__name__}, want ValueError"
        return f"FAIL: percent {bad} accepted, want ValueError"
    return "PASS"


if __name__ == "__main__":
    print(main(sys.argv[1]))
