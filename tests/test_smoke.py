"""Smoke test for the legit happy path.

This walks the normal flow a caller follows: hand a product url to
POST /products, read it back, see it in the list, then delete it. It
does not poke at the buggy edges. Use it as the reference for how the
service is meant to behave and how to stub the network fetch.
"""

from tests.conftest import SAMPLE

DP_URL = "https://www.amazon.com/dp/B07PXGQC1Q"
ASIN = "B07PXGQC1Q"


def test_add_then_read_back(client, stub_fetch):
    stub_fetch(SAMPLE)

    resp = client.post("/products", json={"url": DP_URL})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["asin"] == ASIN
    assert body["title"] == SAMPLE["title"]
    assert body["price"] == SAMPLE["price"]

    got = client.get(f"/products/{ASIN}")
    assert got.status_code == 200
    assert got.get_json()["title"] == SAMPLE["title"]


def test_list_contains_product(client, stub_fetch):
    stub_fetch(SAMPLE)
    client.post("/products", json={"url": DP_URL})

    listing = client.get("/products")
    assert listing.status_code == 200
    asins = [p["asin"] for p in listing.get_json()]
    assert ASIN in asins


def test_delete_removes_product(client, stub_fetch):
    stub_fetch(SAMPLE)
    client.post("/products", json={"url": DP_URL})

    deleted = client.delete(f"/products/{ASIN}")
    assert deleted.status_code == 200

    missing = client.get(f"/products/{ASIN}")
    assert missing.status_code == 404


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
