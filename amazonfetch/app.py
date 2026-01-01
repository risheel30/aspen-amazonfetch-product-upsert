import os

from flask import Flask, g, jsonify, request

from . import fetcher, store
from .asin import extract_asin

DEFAULT_DB_PATH = os.environ.get("AMAZONFETCH_DB", "amazonfetch.db")


def create_app(db_path=None):
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or DEFAULT_DB_PATH

    boot = store.connect(app.config["DB_PATH"])
    store.init_db(boot)
    boot.close()

    def get_conn():
        if "conn" not in g:
            g.conn = store.connect(app.config["DB_PATH"])
        return g.conn

    @app.teardown_appcontext
    def _close(_exc):
        conn = g.pop("conn", None)
        if conn is not None:
            conn.close()

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/products")
    def add_product():
        body = request.get_json(silent=True) or {}
        url = body.get("url")
        if not url:
            return jsonify({"error": "url is required"}), 400

        asin = extract_asin(url)
        if not asin:
            return jsonify({"error": "invalid url, missing ASIN"}), 400
        details = fetcher.fetch_product(url)
        conn = get_conn()

        existing = store.get_by_url(conn, url) or store.get_by_asin(conn, asin)
        if existing:
            product = store.update(conn, existing["asin"], details)
            return jsonify(product), 200

        product = store.insert(conn, asin, url, details)
        return jsonify(product), 201

    @app.get("/products")
    def list_all():
        conn = get_conn()
        return jsonify(store.list_products(conn))

    @app.get("/products/<asin>")
    def get_one(asin):
        conn = get_conn()
        product = store.get_by_asin(conn, asin)
        if product is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(product)

    @app.delete("/products/<asin>")
    def delete_one(asin):
        conn = get_conn()
        removed = store.delete(conn, asin)
        if not removed:
            return jsonify({"error": "not found"}), 404
        return jsonify({"deleted": asin})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
