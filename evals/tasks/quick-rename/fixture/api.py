"""Tiny request router: looks handlers up by resource kind."""
import users


def handle(kind, *args):
    handler = getattr(users, "get_" + kind)
    return handler(*args)
