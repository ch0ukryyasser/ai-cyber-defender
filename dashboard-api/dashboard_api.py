from flask import Flask, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import json
import os
import glob

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALERTS_CSV = os.path.join(BASE_DIR, "..", "ai-response", "alerts_analyzed.csv")
BLACKLIST_CSV = os.path.join(BASE_DIR, "..", "response", "blacklist.csv")
LOGS_CSV = os.path.join(BASE_DIR, "..", "detection", "parsed_logs.csv")

# Dossiers explicites a scanner pour les rapports PDF (pas toute la racine du systeme)
REPORTS_SEARCH_DIRS = [
    os.path.join(BASE_DIR, "..", "response", "incidents"),
    "/response/incidents",
]


def parse_actions(actions_str):
    try:
        return json.loads(actions_str)
    except (json.JSONDecodeError, TypeError):
        return []


def extract_severity(actions):
    for action in actions:
        if action.get("tool") == "send_alert":
            return action.get("input", {}).get("severity", "unknown")
    return "unknown"


def extract_blocked(actions):
    return any(action.get("tool") == "block_ip" for action in actions)


@app.route("/api/alerts")
def get_alerts():
    if not os.path.exists(ALERTS_CSV):
        return jsonify({"error": f"Fichier introuvable: {ALERTS_CSV}"}), 404

    df = pd.read_csv(ALERTS_CSV)
    alerts = []

    for _, row in df.iterrows():
        actions = parse_actions(row.get("actions_taken", "[]"))
        alerts.append({
            "type": row.get("type"),
            "ip": row.get("ip"),
            "first_seen": row.get("first_seen"),
            "last_seen": row.get("last_seen"),
            "severity": extract_severity(actions),
            "blocked": extract_blocked(actions),
            "reasoning": row.get("reasoning"),
            "actions": [a.get("tool") for a in actions],
        })

    alerts.sort(key=lambda a: a["last_seen"], reverse=True)
    return jsonify(alerts)


@app.route("/api/blocked-ips")
def get_blocked_ips():
    if not os.path.exists(BLACKLIST_CSV):
        return jsonify([])

    df = pd.read_csv(BLACKLIST_CSV)
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/traffic")
def get_traffic():
    if not os.path.exists(LOGS_CSV):
        return jsonify({"error": f"Fichier introuvable: {LOGS_CSV}"}), 404

    df = pd.read_csv(LOGS_CSV)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["minute"] = df["timestamp"].dt.floor("min")

    counts = df.groupby("minute").size().reset_index(name="requests")
    counts = counts.sort_values("minute")

    result = [
        {"time": row["minute"].strftime("%Y-%m-%d %H:%M"), "requests": int(row["requests"])}
        for _, row in counts.iterrows()
    ]
    return jsonify(result)


def find_reports():
    seen = {}
    for d in REPORTS_SEARCH_DIRS:
        if not os.path.isdir(d):
            continue
        for f in glob.glob(os.path.join(d, "incident_*.pdf")):
            filename = os.path.basename(f)
            seen[filename] = f
    return seen


@app.route("/api/reports")
def list_reports():
    found = find_reports()
    reports = [
        {
            "filename": filename,
            "modified": os.path.getmtime(path),
            "download_url": f"/api/reports/{filename}",
        }
        for filename, path in found.items()
    ]
    reports.sort(key=lambda r: r["modified"], reverse=True)
    return jsonify(reports)


@app.route("/api/reports/<filename>")
def download_report(filename):
    found = find_reports()
    if filename not in found:
        return jsonify({"error": "Rapport introuvable"}), 404
    return send_file(found[filename], as_attachment=False, mimetype="application/pdf")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
