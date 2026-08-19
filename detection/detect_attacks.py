"""
detect_attacks.py - Phase 2, Étape 2 : Règles de détection

Lit parsed_logs.csv (généré par parse_logs.py) et applique 3 règles :
  1. Bruteforce : +10 requêtes vers /login en 1 minute depuis la même IP
  2. Injection  : motifs suspects (SQLi, XSS, path traversal...) dans l'URL
  3. Scanning   : beaucoup d'URLs différentes en peu de temps depuis une IP

Sauvegarde les alertes détectées dans alerts.csv
"""

import re
import pandas as pd
from pathlib import Path

INPUT_CSV = Path(__file__).parent / "parsed_logs.csv"
OUTPUT_CSV = Path(__file__).parent / "alerts.csv"

# --- Seuils configurables ---
BRUTEFORCE_THRESHOLD = 10      # requêtes /login
BRUTEFORCE_WINDOW = "1min"
SCANNING_THRESHOLD = 15        # URLs distinctes
SCANNING_WINDOW = "1min"

INJECTION_PATTERNS = [
    r"'\s*OR\s*1\s*=\s*1",
    r"UNION\s+SELECT",
    r"<script",
    r"javascript:",
    r"\.\./",          # path traversal
    r"DROP\s+TABLE",
]
INJECTION_REGEX = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(INPUT_CSV, parse_dates=["timestamp"])
    df = df.dropna(subset=["timestamp", "ip", "url"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def detect_bruteforce(df: pd.DataFrame) -> list[dict]:
    """+10 requêtes /login en 1 minute depuis la même IP."""
    alerts = []
    login_df = df[df["url"].str.contains("/login", case=False, na=False)]

    for ip, group in login_df.groupby("ip"):
        group = group.set_index("timestamp")
        counts = group["method"].rolling(BRUTEFORCE_WINDOW).count()
        breaches = counts[counts >= BRUTEFORCE_THRESHOLD]
        if not breaches.empty:
            last_seen = breaches.index.max()
            first_seen = last_seen - pd.Timedelta(BRUTEFORCE_WINDOW)
            alerts.append({
                "type": "BRUTEFORCE",
                "ip": ip,
                "first_seen": first_seen,
                "last_seen": last_seen,
                "count": int(breaches.max()),
                "detail": f"{int(breaches.max())} requêtes /login en {BRUTEFORCE_WINDOW}",
            })
    return alerts


def detect_injection(df: pd.DataFrame) -> list[dict]:
    """Motifs SQLi / XSS / traversal dans l'URL."""
    alerts = []
    matches = df[df["url"].apply(lambda u: bool(INJECTION_REGEX.search(str(u))))]
    for _, row in matches.iterrows():
        alerts.append({
            "type": "INJECTION",
            "ip": row["ip"],
            "first_seen": row["timestamp"],
            "last_seen": row["timestamp"],
            "count": 1,
            "detail": f"Motif suspect dans l'URL : {row['url']}",
        })
    return alerts


def detect_scanning(df: pd.DataFrame) -> list[dict]:
    """Beaucoup d'URLs distinctes en peu de temps depuis la même IP."""
    alerts = []
    for ip, group in df.groupby("ip"):
        group = group.set_index("timestamp").copy()
        # pandas rolling().apply() n'accepte pas le texte : on convertit chaque URL
        # en code numérique (ex: "/login" -> 0, "/search" -> 1...) juste pour compter
        # le nombre de valeurs DISTINCTES dans la fenêtre glissante.
        group["url_code"] = pd.factorize(group["url"])[0]
        distinct_counts = group["url_code"].rolling(SCANNING_WINDOW).apply(
            lambda x: pd.Series(x).nunique(), raw=True
        )
        breaches = distinct_counts[distinct_counts >= SCANNING_THRESHOLD]
        if not breaches.empty:
            last_seen = breaches.index.max()
            first_seen = last_seen - pd.Timedelta(SCANNING_WINDOW)
            alerts.append({
                "type": "SCANNING",
                "ip": ip,
                "first_seen": first_seen,
                "last_seen": last_seen,
                "count": int(breaches.max()),
                "detail": f"{int(breaches.max())} URLs distinctes en {SCANNING_WINDOW}",
            })
    return alerts


def main():
    print(f"[*] Lecture de : {INPUT_CSV}")
    if not INPUT_CSV.exists():
        print(f"[ERREUR] Fichier introuvable : {INPUT_CSV}")
        print("        Lance d'abord parse_logs.py pour générer ce fichier.")
        return

    df = load_data()
    print(f"[+] {len(df)} lignes chargées.\n")

    all_alerts = []
    all_alerts += detect_bruteforce(df)
    all_alerts += detect_injection(df)
    all_alerts += detect_scanning(df)

    if not all_alerts:
        print("[+] Aucune alerte détectée.")
        return

    alerts_df = pd.DataFrame(all_alerts)
    alerts_df = alerts_df.sort_values("first_seen").reset_index(drop=True)

    print(f"[!] {len(alerts_df)} alertes détectées :\n")
    print(alerts_df.to_string(index=False))

    alerts_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[+] Alertes sauvegardées dans : {OUTPUT_CSV}")

    print("\n--- Résumé par type ---")
    print(alerts_df["type"].value_counts().to_string())


if __name__ == "__main__":
    main()