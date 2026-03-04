import os
import json
import time
import requests
from dotenv import load_dotenv

# Load credentials
load_dotenv()
USERNAME = os.getenv("INSTAGRAM_USERNAME") or os.getenv("IG_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD") or os.getenv("IG_PASSWORD")


def get_followers_instagrapi():
    """
    Uses instagrapi — Instagram's private mobile API — to get followers.
    No browser needed. Works perfectly in headless Docker containers.
    """
    from instagrapi import Client
    from instagrapi.exceptions import (
        LoginRequired, ChallengeRequired, BadPassword, PleaseWaitFewMinutes
    )

    print(f"[Instagrapi] Iniciando sesión como: {USERNAME}")
    cl = Client()
    cl.delay_range = [1, 3]  # Human-like delays

    # Try to reuse an existing session if available
    session_file = "ig_session.json"
    logged_in = False

    if os.path.exists(session_file):
        try:
            print("[Instagrapi] Cargando sesión guardada...")
            cl.load_settings(session_file)
            cl.login(USERNAME, PASSWORD)
            print("[Instagrapi] Sesión restaurada correctamente.")
            logged_in = True
        except Exception as e:
            print(f"[Instagrapi] Sesión caducada, relogueando: {e}")
            cl = Client()
            cl.delay_range = [1, 3]

    if not logged_in:
        try:
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(session_file)
            print("[Instagrapi] Login exitoso. Sesión guardada.")
        except BadPassword:
            raise Exception("Contraseña incorrecta para Instagram. Verifica INSTAGRAM_PASSWORD.")
        except ChallengeRequired:
            raise Exception("Instagram exige verificación (challenge). Prueba a iniciar sesión manualmente una vez desde la app oficial.")
        except PleaseWaitFewMinutes:
            raise Exception("Instagram ha bloqueado temporalmente el login. Espera unos minutos.")

    # Get our own user ID
    user_id = cl.user_id_from_username(USERNAME)
    print(f"[Instagrapi] User ID de @{USERNAME}: {user_id}")

    # Get followers
    print("[Instagrapi] Obteniendo seguidores (esto puede tardar)...")
    followers_raw = cl.user_followers(user_id, amount=0)  # 0 = all followers
    followers = sorted([user.username for user in followers_raw.values()])

    print(f"[Instagrapi] Se han encontrado {len(followers)} seguidores.")
    print("--- LISTA DE SEGUIDORES ---")
    for f in followers:
        print(f"  {f}")
    print("---------------------------")

    return followers


def save_and_compare(new_followers_list):
    db_path = "followers.json"

    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            old_followers = set(json.load(f))
    else:
        old_followers = set()

    current_followers = set(new_followers_list)
    new_ones = current_followers - old_followers
    unfollowed = old_followers - current_followers

    if old_followers:
        if new_ones:
            print(f"\n[+] NUEVOS SEGUIDORES ({len(new_ones)}):")
            for fan in sorted(new_ones):
                print(f"  + {fan}")
        else:
            print("\n[=] No hay nuevos seguidores desde la última revisión.")

        if unfollowed:
            print(f"\n[-] UNFOLLOWERS ({len(unfollowed)}):")
            for quitter in sorted(unfollowed):
                print(f"  - {quitter}")
    else:
        print("\n[*] Primera ejecución: Guardando lista inicial de seguidores.")

    results = {
        "new_followers": sorted(list(new_ones)),
        "unfollowers": sorted(list(unfollowed)),
        "first_run": not bool(old_followers)
    }

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(sorted(list(current_followers)), f, indent=4)

    return results


def run_bot():
    """Main function to run the bot and return results."""
    if not USERNAME or not PASSWORD:
        return {
            "success": False,
            "error": "Faltan variables de entorno: INSTAGRAM_USERNAME o INSTAGRAM_PASSWORD no están configuradas."
        }

    try:
        f_list = get_followers_instagrapi()
        results = save_and_compare(f_list)

        payload = {
            "success": True,
            "followers": f_list,
            "changes": results
        }

        # N8N Integration: Send results via webhook if configured
        webhook_url = os.getenv("N8N_WEBHOOK_URL")
        if webhook_url:
            try:
                print(f"[Webhook] Enviando resultados a n8n: {webhook_url}")
                webhook_payload = {
                    "username": USERNAME,
                    "followers_count": len(f_list),
                    "new_followers": results["new_followers"],
                    "unfollowers": results["unfollowers"],
                    "first_run": results["first_run"],
                    "timestamp": time.time()
                }
                resp = requests.post(webhook_url, json=webhook_payload, timeout=10)
                print(f"[Webhook] Respuesta n8n: {resp.status_code}")
                payload["n8n_webhook_status"] = resp.status_code
            except Exception as webhook_err:
                print(f"[Webhook] Error al enviar a n8n: {webhook_err}")
                payload["n8n_webhook_error"] = str(webhook_err)

        return payload

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    result = run_bot()
    print(result)
