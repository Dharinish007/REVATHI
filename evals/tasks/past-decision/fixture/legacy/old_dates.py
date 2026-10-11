"""Old date helpers (previous version)."""
from datetime import date


def parse_date(text):
    """Parse 'YYYY-MM-DD' into a date."""
    year, month, day = text.strip().split("-")
    return date(int(year), int(month), int(day))
