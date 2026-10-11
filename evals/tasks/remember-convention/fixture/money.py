"""Money helpers. All amounts in this project are integer cents."""
from decimal import ROUND_HALF_UP, Decimal


def round_half_up(value):
    """Round a cents value to a whole cent, halves going up (500.5 -> 501). Use this, not round()."""
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def format_cents(cents):
    return f"${cents // 100}.{cents % 100:02d}"
