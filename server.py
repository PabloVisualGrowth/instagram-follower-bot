from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import traceback

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/run-bot", methods=["POST"])
def execute_bot():
    try:
        print("Iniciando ejecución del bot vía API...")
        from instagram_bot import run_bot
        results = run_bot()
        return jsonify(results)
    except Exception as e:
        print(f"Error al ejecutar el bot: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/screenshots/<path:filename>")
def get_screenshot(filename):
    return send_from_directory(".", filename)

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    port = int(os.environ.get("PORT", 8080))
    print(f"Servidor iniciado en http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", debug=False, port=port)
