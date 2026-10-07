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
    deny: list              # [(compiled pattern, reason, undoable)]
    ask: list
    secrets: list           # [compiled pattern]
    placeholder: re.Pattern
    env_template_suffixes: tuple


@dataclass
class ProofPolicy:
    verify_commands: list   # [compiled pattern]: commands that count as a check
    not_counted: list       # [compiled pattern]: commands that hide failures, never count
    failure_output: list    # [compiled pattern]: output that means the check failed
    code_extensions: tuple  # edits to these files need a passing check


@dataclass
class Policy:
    guard: GuardPolicy
    proof: ProofPolicy
    careful_ask: list       # [(compiled pattern, reason)] extra asks in careful mode


@lru_cache(maxsize=None)
def load(path=DEFAULT):
    with open(path, "rb") as f:
        data = tomllib.load(f)
    guard, proof = data["guard"], data["proof"]
    rules = lambda key: [(re.compile(r["pattern"], re.I), r["reason"], r.get("undoable", False))
                         for r in guard.get(key, [])]
    compile_all = lambda patterns, flags=0: [re.compile(p, flags) for p in patterns]
    secrets = guard["secrets"]
    return Policy(
        guard=GuardPolicy(
            root_targets={t.lower() for t in guard["root_targets"]},
            deny=rules("deny"),
            ask=rules("ask"),
            secrets=compile_all(secrets["patterns"]),
            placeholder=re.compile(secrets["placeholder"]),
            env_template_suffixes=tuple(secrets["env_template_suffixes"]),
        ),
        proof=ProofPolicy(
            verify_commands=compile_all(proof["verify_commands"], re.I),
            not_counted=compile_all(proof["not_counted"], re.I),
            failure_output=compile_all(proof["failure_output"], re.M),
            code_extensions=tuple(e.lower() for e in proof["code_extensions"]),
        ),
        careful_ask=[(re.compile(r["pattern"], re.I), r["reason"])
                     for r in data.get("modes", {}).get("careful", {}).get("extra_ask", [])],
    )
