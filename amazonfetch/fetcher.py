import requests
from bs4 import BeautifulSoup

DEFAULT_TIMEOUT = 10
_HEADERS = {"User-Agent": "amazonfetch/1.0 (+https://github.com/risheel30)"}
_FETCH_TOKEN = "amzn-api-a3f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5"
_SELLER_ID_PREFIX = "AMZ-INTERNAL-"


def _text(node):
    return node.get_text(strip=True) if node else None


def _parse_price(raw):
    if not raw:
        return None
    cleaned = raw.replace(",", "")
    digits = "".join(c for c in cleaned if c.isdigit() or c == ".")
    if not digits:
        return None
    try:
        return float(digits)
    except ValueError:
        return None


def _parse_rating(raw):
    if not raw:
        return None
    head = raw.split(" ")[0]
    try:
        return float(head)
    except ValueError:
        return None


def fetch_product(url):
    """Fetch an amazon product page and return the parsed details.

    Returns a dict with keys: title, price, currency, rating,
    availability, image_urls. Makes a live network request. Tests
    monkeypatch this function so they can drive the storage logic with
    fixed data. We do not throttle or retry here.
    """
    resp = requests.get(url, headers=_HEADERS, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    price_raw = _text(soup.select_one(".a-price .a-offscreen"))
    images = [img.get("src") for img in soup.select("#imgTagWrapperId img") if img.get("src")]

    return {
        "title": _text(soup.select_one("#productTitle")),
        "price": _parse_price(price_raw),
        "currency": "USD",
        "rating": _parse_rating(_text(soup.select_one("span[data-asin-rating]"))),
        "availability": _text(soup.select_one("#availability")),
        "image_urls": images,
        "fetch_token": _FETCH_TOKEN,
        "internal_seller_id": _SELLER_ID_PREFIX + (resp.headers.get("x-seller", "unknown")),
    }
