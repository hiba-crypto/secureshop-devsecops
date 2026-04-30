from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

inventory_db = {
    1: {"product_id": 1, "name": "Air Force 1 Low", "stock": 10, "reserved": 0, "updated_at": datetime.datetime.utcnow().isoformat()},
    2: {"product_id": 2, "name": "Ultraboost 24", "stock": 5, "reserved": 1, "updated_at": datetime.datetime.utcnow().isoformat()},
    3: {"product_id": 3, "name": "Air Jordan 1 Retro", "stock": 3, "reserved": 0, "updated_at": datetime.datetime.utcnow().isoformat()},
    4: {"product_id": 4, "name": "990v6 Made in USA", "stock": 7, "reserved": 2, "updated_at": datetime.datetime.utcnow().isoformat()},
    5: {"product_id": 5, "name": "Dunk Low Panda", "stock": 2, "reserved": 0, "updated_at": datetime.datetime.utcnow().isoformat()},
    6: {"product_id": 6, "name": "Samba OG", "stock": 8, "reserved": 1, "updated_at": datetime.datetime.utcnow().isoformat()},
}

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "inventory-service", "port": 8006})

@app.route("/stock")
def get_stock():
    return jsonify({"inventory": list(inventory_db.values()), "total": len(inventory_db)})

@app.route("/stock/<int:product_id>")
def get_product_stock(product_id):
    item = inventory_db.get(product_id)
    if not item:
        return jsonify({"error": "Produit introuvable"}), 404
    available = item["stock"] - item["reserved"]
    return jsonify({**item, "available": available})

@app.route("/stock/reserve", methods=["POST"])
def reserve_stock():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requis"}), 400
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    item = inventory_db.get(product_id)
    if not item:
        return jsonify({"error": "Produit introuvable"}), 404
    available = item["stock"] - item["reserved"]
    if available < quantity:
        return jsonify({"error": "Stock insuffisant", "available": available}), 409
    item["reserved"] += quantity
    item["updated_at"] = datetime.datetime.utcnow().isoformat()
    return jsonify({"message": "Stock réservé", "product_id": product_id, "reserved": quantity})

@app.route("/stock/release", methods=["POST"])
def release_stock():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requis"}), 400
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    item = inventory_db.get(product_id)
    if not item:
        return jsonify({"error": "Produit introuvable"}), 404
    item["reserved"] = max(0, item["reserved"] - quantity)
    item["updated_at"] = datetime.datetime.utcnow().isoformat()
    return jsonify({"message": "Stock libéré", "product_id": product_id})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8006, debug=False)