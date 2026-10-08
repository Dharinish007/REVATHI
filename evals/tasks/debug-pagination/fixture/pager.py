import math


def paginate(items, page, per_page=10):
    """Return the items on a 1-indexed page."""
    start = page * per_page
    return items[start:start + per_page]


def page_count(items, per_page=10):
    return math.ceil(len(items) / per_page)


def all_pages(items, per_page=10):
    pages, page = [], 1
    while True:
        chunk = paginate(items, page, per_page)
        if not chunk:
            break
        pages.append(chunk)
        page += 1
    return pages
