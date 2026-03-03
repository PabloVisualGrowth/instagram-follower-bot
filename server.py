from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
from instagram_bot import run_bot

app = Flask(__name__, template_folder=".")
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run-bot", methods=["POST"])
def execute_bot():
    print("Iniciando ejecución del bot vía API...")
    results = run_bot()
    return jsonify(results)

@app.route("/screenshots/<path:filename>")
def get_screenshot(filename):
    return send_from_directory(".", filename)

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"Servidor iniciado en http://localhost:{port}")
    app.run(host="0.0.0.0", port=port)
