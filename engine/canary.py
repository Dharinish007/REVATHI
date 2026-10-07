"""Canary: a fake credentials file with a unique fake key. A normal task never needs it.

If the agent reads the decoy, something may be steering it (e.g. instructions hidden in a web page): ask the user.
If the fake key appears in any action (a command, a file, a web request), it is being leaked: deny.
State: $REVATHI_HOME/canary.json = {"token": ..., "decoys": [paths]}. Nothing is planted unless the user runs `plant`.
"""
import json
import secrets
import string
from pathlib import Path

from engine import log
from engine.event import Decision

DECOY_NAME = "credentials.backup"


def _state_file():
    return log.home() / "canary.json"


def state():
    try:
        return json.loads(_state_file().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def plant(directory):
    """Create (or reuse) the token and write a decoy file into directory. Returns the decoy path."""
    data = state()
    if not data.get("token"):
        alphabet = string.ascii_uppercase + string.digits
        data = {"token": "AKIA" + "".join(secrets.choice(alphabet) for _ in range(16)), "decoys": []}
    decoy = (Path(directory) / DECOY_NAME).resolve()
    decoy.write_text("# backup of cloud credentials\n[default]\n"
                     f"aws_access_key_id = {data['token']}\n"
                     f"aws_secret_access_key = {secrets.token_urlsafe(30)}\n", encoding="utf-8")
    if str(decoy) not in data["decoys"]:
        data["decoys"].append(str(decoy))
    _state_file().parent.mkdir(parents=True, exist_ok=True)
    _state_file().write_text(json.dumps(data, indent=1), encoding="utf-8")
    return decoy


def check(tool_input):
    """Return a Decision if this action touches a canary, else None. tool_input: the tool's raw arguments."""
    data = state()
    token = data.get("token")
    if not token:
        return None
    text = json.dumps(tool_input, ensure_ascii=False)
    if token in text:
        return Decision("deny", "a planted fake key (canary) is in this action, so something is trying to leak "
                                "credentials. This often means instructions hidden in a web page or file are steering "
                                "the agent. Stop and check what the agent read recently")
    normalized = text.replace("\\\\", "/").replace("\\", "/").lower()
    for decoy in data.get("decoys", []):
        if decoy.replace("\\", "/").lower() in normalized or DECOY_NAME in normalized:
            return Decision("ask", f"the agent wants to touch a decoy file ({DECOY_NAME}) that no normal task needs. "
                                   "Instructions hidden in a web page or file may be steering it. Allow only if you asked for this")
    return None
