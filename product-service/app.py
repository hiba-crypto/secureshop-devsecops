from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PRODUCTS = [
    {"id": 1, "name": "Air Force 1 Low", "brand": "Nike", "price": 16500, "stock": 10, "category": "sneakers", "sizes": ["40","41","42","43","44"]},
    {"id": 2, "name": "Ultraboost 24", "brand": "Adidas", "price": 19800, "stock": 5, "category": "running", "sizes": ["39","40","41","42"]},
    {"id": 3, "name": "Air Jordan 1 Retro", "brand": "Jordan", "price": 24500, "stock": 3, "category": "basketball", "sizes": ["41","42","43","44","45"]},
    {"id": 4, "name": "990v6 Made in USA", "brand": "New Balance", "price": 21000, "stock": 7, "category": "lifestyle", "sizes": ["40","41","42","43"]},
    {"id": 5, "name": "Dunk Low Panda", "brand": "Nike", "price": 17500, "stock": 2, "category": "sneakers", "sizes": ["38","39","40","41","42"]},
    {"id": 6, "name": "Samba OG", "brand": "Adidas", "price": 14900, "stock": 8, "category": "lifestyle", "sizes": ["40","41","42","43"]},
]

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "product-service", "port": 8002})

@app.route("/products")
def get_products():
    category = request.args.get("category")
    brand = request.args.get("brand")
    result = PRODUCTS
    if category:
        result = [p for p in result if p["category"] == category]
    if brand:
        result = [p for p in result if p["brand"].lower() == brand.lower()]
    return jsonify({"products": result, "total": len(result)})

@app.route("/products/<int:product_id>")
def get_product(product_id):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Produit introuvable"}), 404
    return jsonify(product)

@app.route("/products/search")
def search_products():
    query = request.args.get("q", "").lower()
    result = [p for p in PRODUCTS if query in p["name"].lower() or query in p["brand"].lower()]
    return jsonify({"products": result, "query": query})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002, debug=False)