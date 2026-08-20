"""
process_alerts.py - Pont Phase 2 -> Phase 3
=============================================

Lit alerts.csv (produit par detect_attacks.py, Phase 2) et, pour chaque
alerte, appelle l'agent IA (ai_response.py, Phase 3) pour obtenir une
analyse structurée + déclencher les actions automatiques (block_ip,
send_alert, create_ticket) quand pertinent.

Prérequis : ai_response.py doit être dans le MÊME dossier que ce script.
            alerts.csv et parsed_logs.csv doivent être accessibles
            (chemins configurables ci-dessous).

Usage :
    python process_alerts.py
"""

import json
from pathlib import Path

import pandas as pd

# On réutilise directement les fonctions et TOOLS de la Phase 3
from ai_response import analyze_alert_agent, analyze_alert_simple

# On réutilise le même regex que detect_attacks.py (Phase 2) pour rester cohérent
# quand on extrait les lignes de logs pertinentes à afficher au LLM
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "detection"))
from detect_attacks import INJECTION_REGEX  # noqa: E402

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------

# Par défaut on suppose que detection/ est un dossier voisin de ai-response/
# Structure attendue :
#   ai-cyber-defender/
#     detection/
#       alerts.csv
#       parsed_logs.csv
#     ai-response/
#       ai_response.py
#       process_alerts.py   <- ce fichier

DETECTION_DIR = Path(__file__).parent.parent / "detection"
ALERTS_CSV = DETECTION_DIR / "alerts.csv"
PARSED_LOGS_CSV = DETECTION_DIR / "parsed_logs.csv"
OUTPUT_CSV = Path(__file__).parent / "alerts_analyzed.csv"

# Combien de lignes de logs bruts entourant l'alerte on envoie au LLM
# comme "preuve" (ni trop peu -> pas assez de contexte, ni trop -> gaspille des tokens)
MAX_LOG_LINES = 8


# ---------------------------------------------------------------------------
# Construction du contexte pour chaque alerte
# ---------------------------------------------------------------------------

def build_log_excerpt(parsed_logs: pd.DataFrame, ip: str, first_seen, last_seen, alert_type: str = "") -> str:
    """
    Récupère les vraies lignes de logs de cette IP dans la fenêtre de l'alerte,
    pour donner au LLM un contexte réel plutôt qu'un résumé.

    Priorise les lignes réellement pertinentes pour le type d'alerte (ex: /login
    pour BRUTEFORCE, motifs suspects pour INJECTION) plutôt que de prendre
    bêtement les N premières lignes chronologiques — sinon, si l'IP est bavarde
    sur d'autres endpoints dans la même fenêtre (typiquement 172.17.0.1, la
    passerelle Docker), les lignes pertinentes peuvent être noyées.
    """
    window = parsed_logs[
        (parsed_logs["ip"] == ip)
        & (parsed_logs["timestamp"] >= first_seen)
        & (parsed_logs["timestamp"] <= last_seen)
    ].sort_values("timestamp")

    if window.empty:
        return "(aucune ligne de log correspondante trouvée)"

    if alert_type == "BRUTEFORCE":
        priority = window[window["url"].str.contains("/login", case=False, na=False)]
    elif alert_type == "INJECTION":
        priority = window[window["url"].apply(lambda u: bool(INJECTION_REGEX.search(str(u))))]
    else:
        priority = window  # SCANNING : la diversité des URLs est le signal, pas de filtre

    # On complète avec le reste de la fenêtre si la partie "pertinente" ne remplit
    # pas le quota, pour garder un peu de contexte autour.
    rest = window.drop(priority.index)
    ordered = pd.concat([priority, rest]).head(MAX_LOG_LINES).sort_values("timestamp")

    lines = []
    for _, row in ordered.iterrows():
        method = row.get("method", "?")
        url = row.get("url", "?")
        ts = row.get("timestamp", "?")
        lines.append(f'{ip} - - [{ts}] "{method} {url}"')

    return "\n".join(lines)


def alert_row_to_dict(row: pd.Series, parsed_logs: pd.DataFrame) -> dict:
    """Convertit une ligne d'alerts.csv au format attendu par ai_response.py."""
    return {
        "source_ip": row["ip"],
        "timestamp": str(row["last_seen"]),
        "pattern_detected": f"[{row['type']}] {row['detail']} (count={row['count']})",
        "log_excerpt": build_log_excerpt(parsed_logs, row["ip"], row["first_seen"], row["last_seen"], alert_type=row["type"]),
    }


# ---------------------------------------------------------------------------
# Boucle principale
# ---------------------------------------------------------------------------

def main():
    if not ALERTS_CSV.exists():
        print(f"[ERREUR] Fichier introuvable : {ALERTS_CSV}")
        print("        Lance d'abord detect_attacks.py (Phase 2) pour générer alerts.csv.")
        return

    if not PARSED_LOGS_CSV.exists():
        print(f"[ERREUR] Fichier introuvable : {PARSED_LOGS_CSV}")
        print("        Lance d'abord parse_logs.py (Phase 2) pour générer parsed_logs.csv.")
        return

    alerts_df = pd.read_csv(ALERTS_CSV, parse_dates=["first_seen", "last_seen"])
    parsed_logs = pd.read_csv(PARSED_LOGS_CSV, parse_dates=["timestamp"])

    if alerts_df.empty:
        print("[+] alerts.csv est vide, rien à analyser.")
        return

    print(f"[*] {len(alerts_df)} alerte(s) à analyser...\n")

    results = []

    for i, row in alerts_df.iterrows():
        alert = alert_row_to_dict(row, parsed_logs)

        print("=" * 70)
        print(f"Alerte {i + 1}/{len(alerts_df)} : {row['type']} - IP {row['ip']}")
        print("=" * 70)

        analysis = analyze_alert_agent(alert)

        print("Raisonnement:")
        print(analysis["reasoning"])
        print("\nActions exécutées:")
        for action in analysis["actions_taken"]:
            print(f"  - {action['tool']}({action['input']}) -> {action['result']}")
        print()

        results.append({
            "type": row["type"],
            "ip": row["ip"],
            "first_seen": row["first_seen"],
            "last_seen": row["last_seen"],
            "reasoning": analysis["reasoning"],
            "actions_taken": json.dumps(analysis["actions_taken"], ensure_ascii=False),
        })

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[+] Résultats sauvegardés dans : {OUTPUT_CSV}")


if __name__ == "__main__":
    main()