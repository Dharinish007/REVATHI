"""Load and compile the policy file (TOML, read with the standard library)."""
import re
import tomllib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent.parent / "policy" / "default.toml"


@dataclass
class GuardPolicy:
    root_targets: set
    deny: list              # [(compiled pattern, reason)]
    ask: list
    secrets: list           # [compiled pattern]
    placeholder: re.Pattern
    env_template_suffixes: tuple


@lru_cache(maxsize=None)
def load(path=DEFAULT):
    with open(path, "rb") as f:
        guard = tomllib.load(f)["guard"]
    rules = lambda key: [(re.compile(r["pattern"], re.I), r["reason"]) for r in guard.get(key, [])]
    secrets = guard["secrets"]
    return GuardPolicy(
        root_targets={t.lower() for t in guard["root_targets"]},
        deny=rules("deny"),
        ask=rules("ask"),
        secrets=[re.compile(p) for p in secrets["patterns"]],
        placeholder=re.compile(secrets["placeholder"]),
        env_template_suffixes=tuple(secrets["env_template_suffixes"]),
    )
