"""Order calculations."""
from money import round_half_up


def subtotal(items):
    """Sum of price_cents * qty for each item."""
    total = 0
    for item in items:
        if item["qty"] < 0:
            raise ValueError("quantity cannot be negative")
        total += item["price_cents"] * item["qty"]
    return total


def add_tax(total_cents, rate_percent):
    """Total after tax, in cents."""
    if rate_percent < 0:
        raise ValueError("tax rate cannot be negative")
    return round_half_up(total_cents * (100 + rate_percent) / 100)
