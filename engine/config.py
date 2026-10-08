"""User settings in $REVATHI_HOME/config.json (mode, what `revathi install` changed)."""
import json

from engine import log

MODES = ("observe", "careful", "balanced", "full")
DEFAULT_MODE = "balanced"


def path():
    return log.home() / "config.json"


def load():
    try:
        return json.loads(path().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save(data):
    path().parent.mkdir(parents=True, exist_ok=True)
    path().write_text(json.dumps(data, indent=1), encoding="utf-8")


def mode():
    value = load().get("mode", DEFAULT_MODE)
    return value if value in MODES else DEFAULT_MODE


def set_mode(value):
    if value not in MODES:
        raise ValueError(f"mode must be one of {', '.join(MODES)}")
    data = load()
    data["mode"] = value
    save(data)
