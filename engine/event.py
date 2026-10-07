"""Common event format shared by every adapter, so the engine is written once."""
from dataclasses import dataclass, field

COMMAND, WRITE, OTHER = "command", "write", "other"


@dataclass
class Event:
    tool: str                                       # which AI tool sent it, e.g. "claude-code"
    kind: str                                       # COMMAND, WRITE or OTHER
    name: str = ""                                  # the tool's own action name, e.g. "Bash", "run_command"
    command: str = ""                               # shell command (COMMAND)
    path: str = ""                                  # target file (WRITE)
    texts: list = field(default_factory=list)       # new text being written (WRITE)
    raw: dict = field(default_factory=dict)         # the tool's original event, untouched


@dataclass
class Decision:
    verdict: str    # "ask" or "deny" before an action; "block" to stop the agent from finishing
    reason: str     # plain English, shown to the user (and to the agent for "block")
    undoable: bool = False  # the action only changes local files, so a snapshot can reverse it
