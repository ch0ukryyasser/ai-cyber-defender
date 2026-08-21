from response.block_ip import block_ip
from response.discord_alert import send_alert
from response.generate_report import generate_report

def handle_incident(ip: str, attack_type: str, details: str = ""):
    """Point d'entrée appelé quand detect_attacks.py signale une attaque."""
    block_ip(ip, reason=attack_type)
    send_alert(ip, attack_type, details)
    generate_report(ip, attack_type, details, blocked=True)

# Exemple de test manuel
if __name__ == "__main__":
    handle_incident(
        ip="192.168.1.50",
        attack_type="Brute Force",
        details="12 tentatives de login échouées en 60 secondes."
    )