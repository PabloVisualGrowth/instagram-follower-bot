"""
Script para generar la sesión de Instagram de forma local.
Ejecútalo UNA VEZ en tu PC, luego sube el archivo ig_session.json a EasyPanel.
"""
import os
from instagrapi import Client

USERNAME = "testingformanychat"
PASSWORD = "Barcelona1997"

print(f"Iniciando sesión como @{USERNAME}...")
cl = Client()
cl.login(USERNAME, PASSWORD)
cl.dump_settings("ig_session.json")
print(f"✅ Sesión guardada en ig_session.json")
print("Ahora sube este archivo a EasyPanel ejecutando el siguiente comando en tu terminal:")
print(f'  docker cp ig_session.json <container_id>:/app/ig_session.json')
print("O bien, copia el contenido del archivo y créalo manualmente en EasyPanel.")
