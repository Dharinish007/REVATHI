"""Common event format shared by every adapter, so the engine is written once."""
from dataclasses import dataclass, field

COMMAND, WRITE, OTHER = "command", "write", "other"


@dataclass
class Event:
    tool: str                                       # which AI tool sent it, e.g. "claude-code"
    kind: str                                       # COMMAND, WRITE or OTHER
    command: str = ""                               # shell command (COMMAND)
    path: str = ""                                  # target file (WRITE)
    texts: list = field(default_factory=list)       # new text being written (WRITE)
    raw: dict = field(default_factory=dict)         # the tool's original event, untouched


@dataclass
class Decision:
    verdict: str    # "ask" or "deny"; no Decision at all means "no opinion"
    reason: str     # plain English, shown to the user
