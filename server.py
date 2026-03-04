from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import traceback

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/reset-followers", methods=["POST"])
def reset_followers():
    try:
        if os.path.exists("followers.json"):
            os.remove("followers.json")
            return jsonify({"success": True, "message": "Memoria de seguidores eliminada. El próximo scan tratará a todos como nuevos."})
        return jsonify({"success": True, "message": "Ya estaba limpio."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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

@app.route("/send-dms", methods=["POST"])
def send_dms():
    try:
        body = request.get_json() or {}
        usernames = body.get("usernames", [])
        if not usernames:
            return jsonify({"success": False, "error": "No se proporcionaron usuarios."}), 400
        from dm_bot import run_dm_bot
        run_dm_bot(usernames)
        return jsonify({"success": True, "message": f"DMs enviados a {len(usernames)} usuario(s).", "usernames": usernames})
    except Exception as e:
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
