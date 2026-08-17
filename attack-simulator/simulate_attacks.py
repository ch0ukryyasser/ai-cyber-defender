import requests
import time
import random

BASE_URL = "http://localhost:5000"

def simulate_normal_traffic(n=5):
    """Simule du trafic normal d'utilisateurs légitimes."""
    print("→ Génération de trafic normal...")
    for i in range(n):
        requests.get(f"{BASE_URL}/")
        requests.get(f"{BASE_URL}/search", params={"q": "python tutorial"})
        requests.get(f"{BASE_URL}/api/users/{random.randint(1, 100)}")
        time.sleep(0.5)
    print(f"  {n * 3} requêtes normales envoyées.\n")

def simulate_bruteforce(n=20):
    """Simule une attaque bruteforce sur /login."""
    print("→ Simulation d'un bruteforce sur /login...")
    passwords = ["123456", "password", "admin", "qwerty", "letmein",
                 "welcome", "monkey", "dragon", "master", "admin123"]
    for i in range(n):
        pwd = random.choice(passwords)
        requests.post(f"{BASE_URL}/login", data={"username": "admin", "password": pwd})
        time.sleep(0.1)
    print(f"  {n} tentatives de login envoyées.\n")

def simulate_sqli_xss(n=8):
    """Simule des tentatives d'injection SQL et XSS."""
    print("→ Simulation d'injections SQLi/XSS...")
    payloads = [
        "' OR 1=1--",
        "' OR '1'='1",
        "admin'--",
        "1; DROP TABLE users--",
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "'; SELECT * FROM users--",
        "<svg onload=alert(1)>"
    ]
    for payload in payloads[:n]:
        requests.get(f"{BASE_URL}/search", params={"q": payload})
        time.sleep(0.2)
    print(f"  {n} payloads envoyés.\n")

def simulate_scanning(n=15):
    """Simule un scanner cherchant des endpoints (comportement bot)."""
    print("→ Simulation de scanning d'URLs...")
    paths_to_scan = [
        "/admin", "/wp-admin", "/config", "/.env", "/backup",
        "/api/v1", "/test", "/debug", "/console", "/.git",
        "/phpmyadmin", "/login.php", "/uploads", "/tmp", "/api/users/1"
    ]
    for path in paths_to_scan[:n]:
        try:
            requests.get(f"{BASE_URL}{path}", timeout=2)
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.1)
    print(f"  {n} URLs scannées.\n")

if __name__ == "__main__":
    print("=== Simulation de trafic web (normal + malveillant) ===\n")
    simulate_normal_traffic(5)
    simulate_bruteforce(20)
    simulate_sqli_xss(8)
    simulate_scanning(15)
    simulate_normal_traffic(3)
    print("=== Simulation terminée. Vérifie test-server/logs/access.log ===")