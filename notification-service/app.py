from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Notification Service running"})

if __name__ == "__main__":
    app.run(port=8005)