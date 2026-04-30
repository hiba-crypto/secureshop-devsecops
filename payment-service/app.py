from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import random
import string
 
app = Flask(__name__)
CORS(app)
 
# ⚠️ SAST: clé hardcodée intentionnelle pour démonstration Bandit
PAYMENT_SECRET_KEY = "payment-secret-hardcoded-123"
transactions_db = {}
 
def generate_transaction_id():
    return "TXN-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
 
@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "payment-service", "port": 8004})
 
@app.route("/pay", methods=["POST"])
def process_payment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requis"}), 400
 
    amount = data.get("amount", 0)
    order_id = data.get("order_id")
    method = data.get("method", "card")
 
    if not order_id or amount <= 0:
        return jsonify({"error": "order_id et amount requis"}), 400
 
    # Simulation paiement (80% succès)
    success = random.random() > 0.2
    txn_id = generate_transaction_id()
 
    transaction = {
        "id": txn_id,
        "order_id": order_id,
        "amount": amount,
        "method": method,
        "status": "success" if success else "failed",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    transactions_db[txn_id] = transaction
 
    if success:
        return jsonify({"message": "Paiement accepté", "transaction": transaction}), 200
    else:
        return jsonify({"message": "Paiement refusé", "transaction": transaction}), 402
 
@app.route("/transactions")
def get_transactions():
    return jsonify({"transactions": list(transactions_db.values()), "total": len(transactions_db)})
 
@app.route("/transactions/<txn_id>")
def get_transaction(txn_id):
    txn = transactions_db.get(txn_id)
    if not txn:
        return jsonify({"error": "Transaction introuvable"}), 404
    return jsonify(txn)
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004, debug=False)
