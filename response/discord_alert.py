import os
import requests
from dotenv import load_dotenv

load_dotenv()
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

def send_alert(ip: str, attack_type: str, details: str = ""):
    if not DISCORD_WEBHOOK_URL:
        print("[WARN] DISCORD_WEBHOOK_URL non configurée, alerte non envoyée.")
        return False

    embed = {
        "title": f"🚨 Attaque détectée : {attack_type}",
        "color": 15158332,  # rouge
        "fields": [
            {"name": "IP source", "value": ip, "inline": True},
            {"name": "Type", "value": attack_type, "inline": True},
            {"name": "Détails", "value": details or "N/A", "inline": False},
        ],
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=5)

    if response.status_code in (200, 204):
        print(f"[ALERT] Alerte envoyée sur Discord pour {ip}")
        return True
    print(f"[ERROR] Échec envoi Discord: {response.status_code}")
    return False