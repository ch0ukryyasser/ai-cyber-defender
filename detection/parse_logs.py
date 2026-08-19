"""
parse_logs.py - Phase 2 : Parseur de logs pour AI Cyber Defender

Ton access.log contient DEUX formats mélangés (un par requête loggée deux fois) :
  1. Format custom  : 2026-08-17T00:42:22.579875 | IP=172.17.0.1 | POST /login | UA=python-requests/2.34.2
  2. Format Werkzeug : 172.17.0.1 - - [17/Aug/2026 00:42:22] "POST /login HTTP/1.1" 401 -

Ce script essaie les DEUX regex sur chaque ligne, dans cet ordre, et garde
la première qui matche. Rien n'est perdu, peu importe le format de la ligne.
"""

import re
import pandas as pd
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent / "test-server" / "logs" / "access.log"
OUTPUT_CSV = Path(__file__).parent / "parsed_logs.csv"

# Format custom (ton propre logging applicatif)
PATTERN_CUSTOM = re.compile(
    r'^(?P<timestamp>\S+)\s*\|\s*IP=(?P<ip>\S+)\s*\|\s*(?P<method>[A-Z]+)\s+(?P<url>\S+)\s*\|\s*UA=(?P<user_agent>.*)$'
)

# Format par défaut de Werkzeug (logger interne de Flask)
PATTERN_WERKZEUG = re.compile(
    r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - '
    r'\[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<url>\S+) HTTP/[\d.]+" '
    r'(?P<status>\d{3})'
)


def parse_line(line: str) -> dict | None:
    """Essaie le format custom, puis le format Werkzeug. Retourne None si aucun ne matche."""
    m = PATTERN_CUSTOM.search(line)
    if m:
        d = m.groupdict()
        d["source_format"] = "custom"
        return d

    m = PATTERN_WERKZEUG.search(line)
    if m:
        d = m.groupdict()
        d["source_format"] = "werkzeug"
        return d

    return None


def parse_log_file(log_path: Path) -> list[dict]:
    records = []
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            parsed = parse_line(line)
            if parsed:
                records.append(parsed)
            else:
                print(f"[!] Ligne {line_num} non reconnue : {line[:80]}")
    return records


def build_dataframe(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    if df.empty:
        return df

    # Les deux formats n'ont pas exactement le même format de date -> parsing flexible
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", format="mixed")
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def main():
    print(f"[*] Lecture du fichier : {LOG_FILE}")

    if not LOG_FILE.exists():
        print(f"[ERREUR] Fichier introuvable : {LOG_FILE}")
        return

    records = parse_log_file(LOG_FILE)
    df = build_dataframe(records)

    if df.empty:
        print("[!] Aucune ligne n'a pu être parsée.")
        return

    print(f"\n[+] {len(df)} lignes parsées avec succès.\n")
    print(df.head(10).to_string(index=False))

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[+] Résultats sauvegardés dans : {OUTPUT_CSV}")

    print("\n--- Résumé ---")
    print(f"IPs distinctes      : {df['ip'].nunique()}")
    print(f"Formats détectés    : {df['source_format'].value_counts().to_dict()}")
    print(f"Méthodes HTTP       : {df['method'].value_counts().to_dict()}")
    print(f"Période couverte    : {df['timestamp'].min()} -> {df['timestamp'].max()}")


if __name__ == "__main__":
    main()