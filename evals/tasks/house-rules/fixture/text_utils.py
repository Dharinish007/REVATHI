"""Small text helpers for the blog."""


def word_count(text):
    return len(text.split())


def excerpt(text, words=20):
    parts = text.split()
    return " ".join(parts[:words]) + ("…" if len(parts) > words else "")
