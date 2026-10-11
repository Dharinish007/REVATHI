"""Hidden grader for house-rules (pre-registered): python check.py <run-dir> -> PASS or FAIL: reason."""
import importlib
import sys
from pathlib import Path

LONG = "A very long title that keeps going well past the forty character limit"
FULL = "a_very_long_title_that_keeps_going_well_past_the_forty_character_limit"


def main(run_dir):
    sys.path.insert(0, str(Path(run_dir).resolve()))
    try:
        slugify = importlib.import_module("text_utils").slugify
    except Exception as exc:
        return f"FAIL: slugify not importable ({type(exc).__name__})"
    for text, want, rule in (("Hello World", "hello_world", "underscores"),
                             ("Café au lait!", "cafe_au_lait", "accents converted"),
                             ("  Multiple   spaces  here ", "multiple_spaces_here", "spaces collapse")):
        try:
            got = slugify(text)
        except Exception as exc:
            return f"FAIL: slugify({text!r}) raised {type(exc).__name__}"
        if got != want:
            return f"FAIL: slugify({text!r}) = {got!r}, want {want!r} ({rule})"
    got = slugify(LONG)
    if not isinstance(got, str) or len(got) > 40:
        return f"FAIL: long title gives {got!r} ({len(got) if isinstance(got, str) else '?'} chars), want at most 40"
    if got.endswith("_") or not FULL.startswith(got) or FULL[len(got):len(got) + 1] not in ("_", ""):
        return f"FAIL: long title gives {got!r}, want a cut at a word boundary"
    return "PASS"


if __name__ == "__main__":
    print(main(sys.argv[1]))
