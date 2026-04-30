from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

orders_db = {}
order_counter = 1

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "order-service", "port": 8003})

@app.route("/orders", methods=["GET"])
def get_orders():
    user_id = request.args.get("user_id")
    if user_id:
        result = [o for o in orders_db.values() if o["user_id"] == user_id]
    else:
        result = list(orders_db.values())
    return jsonify({"orders": result, "total": len(result)})

@app.route("/orders", methods=["POST"])
def create_order():
    global order_counter
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requis"}), 400

    items = data.get("items", [])
    if not items:
        return jsonify({"error": "Panier vide"}), 400

    order_id = f"ORD-{order_counter:04d}"
    order_counter += 1

    order = {
        "id": order_id,
        "user_id": data.get("user_id", "anonymous"),
        "items": items,
        "total": data.get("total", 0),
        "status": "pending",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    orders_db[order_id] = order
    return jsonify({"message": "Commande créée", "order": order}), 201

@app.route("/orders/<order_id>")
def get_order(order_id):
    order = orders_db.get(order_id)
    if not order:
        return jsonify({"error": "Commande introuvable"}), 404
    return jsonify(order)

@app.route("/orders/<order_id>/status", methods=["PUT"])
def update_status(order_id):
    order = orders_db.get(order_id)
    if not order:
        return jsonify({"error": "Commande introuvable"}), 404
    data = request.get_json()
    status = data.get("status", "pending")
    order["status"] = status
    order["updated_at"] = datetime.datetime.utcnow().isoformat()
    return jsonify({"message": "Statut mis à jour", "order": order})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003, debug=False)