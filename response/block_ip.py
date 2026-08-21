import csv
from pathlib import Path
from datetime import datetime

BLACKLIST_FILE = Path("response/blacklist.csv")

def block_ip(ip: str, reason: str = "unknown"):
    """
    Simule le blocage d'une IP (ajout à une liste noire CSV).
    En prod réelle, on remplacerait ceci par un appel iptables/API firewall.
    """
    BLACKLIST_FILE.parent.mkdir(exist_ok=True)
    is_new_file = not BLACKLIST_FILE.exists()

    with open(BLACKLIST_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new_file:
            writer.writerow(["ip", "reason", "timestamp"])
        writer.writerow([ip, reason, datetime.now().isoformat()])

    print(f"[BLOCK] {ip} ajoutée à la liste noire (raison: {reason})")
    return True

def is_blocked(ip: str) -> bool:
    if not BLACKLIST_FILE.exists():
        return False
    with open(BLACKLIST_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return any(row["ip"] == ip for row in reader)