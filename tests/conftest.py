import pytest

from amazonfetch import fetcher
from amazonfetch.app import create_app

# A realistic fetched payload. Tests copy this and tweak a field so they
# can drive the storage and upsert logic without touching the network.
SAMPLE = {
    "title": "Anker USB-C Charger 65W",
    "price": 39.99,
    "currency": "USD",
    "rating": 4.6,
    "availability": "In Stock",
    "image_urls": [
        "https://m.media-amazon.com/images/I/aaa.jpg",
        "https://m.media-amazon.com/images/I/bbb.jpg",
    ],
    "fetch_token": "amzn-api-a3f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5",
    "internal_seller_id": "AMZ-INTERNAL-S7K2-LIVE-EU",
}


@pytest.fixture
def client(tmp_path):
    app = create_app(db_path=str(tmp_path / "test.db"))
    app.testing = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def stub_fetch(monkeypatch):
    """Return a setter that pins what fetcher.fetch_product returns.

    Usage:
        stub_fetch(SAMPLE)                       # use the sample as-is
        stub_fetch({**SAMPLE, "price": 49.99})   # override a field
    """

    def _set(details):
        monkeypatch.setattr(fetcher, "fetch_product", lambda url: dict(details))
        return details

    return _set
