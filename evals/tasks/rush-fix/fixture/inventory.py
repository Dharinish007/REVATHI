"""Stock helpers."""


def total_value(items):
    """Total value of the stock on hand."""
    return sum(item["price"] for item in items)
