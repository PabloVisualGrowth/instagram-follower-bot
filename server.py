from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
from instagram_bot import run_bot

app = Flask(__name__, static_folder="frontend", template_folder="frontend")
CORS(app) # Enable CORS for frontend development

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

if __name__ == "__main__":
    # Ensure frontend folder exists (we'll create it next)
    if not os.path.exists("frontend"):
        os.makedirs("frontend")
    
    print("Servidor iniciado en http://0.0.0.0:5001")
    app.run(host="0.0.0.0", debug=False, port=5001)
