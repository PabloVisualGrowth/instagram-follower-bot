"""
DM Welcome Bot — Envía un mensaje de bienvenida a nuevos seguidores.
Uso:
    python dm_bot.py                          → Lee nuevos seguidores de new_followers.txt
    python dm_bot.py usuario1 usuario2        → Envía DM a los usuarios indicados
"""

import os
import sys
import time
import random
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("INSTAGRAM_USERNAME") or os.getenv("IG_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD") or os.getenv("IG_PASSWORD")

# ─────────────────────────────────────────────
# MENSAJE DE BIENVENIDA
# ─────────────────────────────────────────────
WELCOME_MESSAGE = """¡Hola! 😊 Gracias por seguirnos y por tu apoyo, la verdad es que nos ayuda mucho para seguir conectando con gente como tu.
Si te apetece, tenemos un regalito para ti: 10% de descuento 🎁
Solo entra en esenciaparadise.com, haz clic en "GET YOUR FULL PASS" y rellena el formulario, nos encantaría darte tu merecido descuento. ✨"""

# ─────────────────────────────────────────────
# ARCHIVO DE REGISTRO (para no enviar DM dos veces)
# ─────────────────────────────────────────────
SENT_LOG = "dm_sent.txt"


def load_sent_log():
    if os.path.exists(SENT_LOG):
        with open(SENT_LOG, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def mark_as_sent(username):
    with open(SENT_LOG, "a") as f:
        f.write(username + "\n")


def send_dm(cl, username):
    try:
        user_id = cl.user_id_from_username(username)
        cl.direct_send(WELCOME_MESSAGE, [user_id])
        print(f"[OK] DM enviado a @{username}")
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo enviar DM a @{username}: {e}")
        return False


def run_dm_bot(usernames):
    if not USERNAME or not PASSWORD:
        print("[ERROR] Faltan INSTAGRAM_USERNAME o INSTAGRAM_PASSWORD en el .env")
        return

    from instagrapi import Client

    print(f"[DM Bot] Iniciando sesión como @{USERNAME}...")
    cl = Client()
    cl.delay_range = [2, 5]

    session_file = "ig_session.json"
    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
            cl.login(USERNAME, PASSWORD)
            print("[DM Bot] Sesión restaurada.")
        except Exception:
            cl = Client()
            cl.delay_range = [2, 5]
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(session_file)
    else:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(session_file)

    sent_log = load_sent_log()
    pending = [u for u in usernames if u not in sent_log]

    if not pending:
        print("[DM Bot] No hay usuarios nuevos a los que enviar DM.")
        return

    print(f"[DM Bot] Enviando DMs a {len(pending)} usuario(s)...")

    for i, username in enumerate(pending):
        print(f"[{i+1}/{len(pending)}] Enviando a @{username}...")
        success = send_dm(cl, username)

        if success:
            mark_as_sent(username)

        # Pausa aleatoria entre DMs para evitar rate limit (entre 30 y 90 segundos)
        if i < len(pending) - 1:
            delay = random.randint(30, 90)
            print(f"   Esperando {delay}s antes del siguiente DM...")
            time.sleep(delay)

    print(f"\n[DM Bot] Completado. DMs enviados exitosamente.")


if __name__ == "__main__":
    # Si se pasan usuarios como argumentos: python dm_bot.py user1 user2
    if len(sys.argv) > 1:
        targets = sys.argv[1:]
    else:
        # Si no, leer de new_followers.txt (uno por línea)
        if os.path.exists("new_followers.txt"):
            with open("new_followers.txt", "r") as f:
                targets = [line.strip() for line in f if line.strip()]
        else:
            print("Uso: python dm_bot.py usuario1 usuario2")
            print("   o crea un archivo new_followers.txt con los usernames (uno por línea)")
            sys.exit(1)

    run_dm_bot(targets)
