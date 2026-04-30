from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt
import datetime
import os
import hashlib

app = Flask(__name__)

# ✅ CORS activé (corrige "Service indisponible" côté frontend)
CORS(app)

# ⚠️ EN PRODUCTION: utiliser HashiCorp Vault (Step 8 du workshop)
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me-in-production")
JWT_EXPIRY_HOURS = 1

# Base de données en mémoire (remplacer par PostgreSQL en prod)
users_db = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id, username, role="user"):
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Token manquant"}), 401
        token = auth.split(" ")[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Token invalide ou expiré"}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "user-service",
        "port": 8001
    })

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requis"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")
    email    = data.get("email", "").strip()

    if not username or not password or not email:
        return jsonify({"error": "username, password et email sont requis"}), 400

    if username in users_db:
        return jsonify({"error": "Utilisateur déjà existant"}), 409

    user_id = str(len(users_db) + 1)
    users_db[username] = {
        "id": user_id,
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "role": "user",
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    token = create_token(user_id, username)
    return jsonify({
        "message": "Inscription réussie",
        "user_id": user_id,
        "username": username,
        "token": token
    }), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requis"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = users_db.get(username)
    if not user or user["password_hash"] != hash_password(password):
        return jsonify({"error": "Identifiants incorrects"}), 401

    token = create_token(user["id"], username, user["role"])
    return jsonify({
        "message": "Connexion réussie",
        "token": token,
        "user": {
            "id": user["id"],
            "username": username,
            "email": user["email"],
            "role": user["role"]
        }
    })

@app.route("/profile", methods=["GET"])
@token_required
def profile():
    username = request.user.get("username")
    user = users_db.get(username)
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404
    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"]
    })

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    token = data.get("token") if data else None
    if not token:
        return jsonify({"valid": False, "error": "Token manquant"}), 400

    payload = verify_token(token)
    if not payload:
        return jsonify({"valid": False, "error": "Token invalide"}), 401

    return jsonify({
        "valid": True,
        "user_id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role")
    })

@app.route("/users", methods=["GET"])
@token_required
def list_users():
    if request.user.get("role") != "admin":
        return jsonify({"error": "Accès refusé"}), 403

    return jsonify([{
        "id": u["id"],
        "username": u["username"],
        "email": u["email"],
        "role": u["role"]
    } for u in users_db.values()])

if __name__ == "__main__":
    # Admin par défaut
    users_db["admin"] = {
        "id": "0",
        "username": "admin",
        "email": "admin@secureshop.com",
        "password_hash": hash_password("admin123"),
        "role": "admin",
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    app.run(host="0.0.0.0", port=8001, debug=False)