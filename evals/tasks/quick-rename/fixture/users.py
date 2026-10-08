"""User records."""

_USERS = {1: "ada", 2: "linus"}


def get_user(uid):
    """Return the user name for an id."""
    return _USERS[uid]


def get_users():
    """Return all user names."""
    return sorted(_USERS.values())
