"""
anomaly_detection.py - Phase 2, Étape 3 (bonus) : détection d'anomalies avec Isolation Forest

Principe : au lieu de règles fixes ("+10 requêtes /login en 1 min"), on entraîne
un modèle qui apprend ce qu'est un volume de trafic "normal" à partir des données,
et signale tout ce qui s'en écarte fortement — sans qu'on ait eu à définir de seuil.

Étapes :
  1. Découper le trafic en fenêtres de temps fixes (1 minute)
  2. Pour chaque fenêtre, calculer 3 features : nb de requêtes, nb d'IPs distinctes,
     nb d'URLs distinctes
  3. Entraîner un Isolation Forest sur ces features
  4. Le modèle isole les points "faciles à séparer du reste" -> ce sont les anomalies

Isolation Forest est bien adapté ici car il n'a pas besoin d'exemples d'attaques
étiquetés à l'avance (apprentissage non supervisé) : il apprend uniquement à partir
du trafic observé.
"""

import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest

INPUT_CSV = Path(__file__).parent / "parsed_logs.csv"
OUTPUT_CSV = Path(__file__).parent / "anomalies_ml.csv"

TIME_BUCKET = "1min"   # taille des fenêtres de temps analysées
CONTAMINATION = 0.15   # proportion attendue d'anomalies dans les données (à ajuster)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(INPUT_CSV, parse_dates=["timestamp"])
    df = df.dropna(subset=["timestamp", "ip", "url"])
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Agrège le trafic par fenêtre de temps et calcule les features pour le modèle."""
    df = df.set_index("timestamp").sort_index()

    features = df.resample(TIME_BUCKET).agg(
        request_count=("ip", "count"),
        distinct_ips=("ip", "nunique"),
        distinct_urls=("url", "nunique"),
    )

    # On ne garde que les fenêtres où il y a eu au moins une requête
    # (les fenêtres vides ne veulent rien dire pour la détection)
    features = features[features["request_count"] > 0]

    return features


def detect_anomalies(features: pd.DataFrame) -> pd.DataFrame:
    if len(features) < 5:
        print("[!] Pas assez de fenêtres de trafic distinctes pour entraîner le modèle "
              "(minimum recommandé : 5). Le résultat sera peu fiable avec aussi peu de données.")

    model = IsolationForest(
        contamination=CONTAMINATION,
        random_state=42,
        n_estimators=100,
    )

    X = features[["request_count", "distinct_ips", "distinct_urls"]]
    features = features.copy()
    features["anomaly_score"] = model.fit_predict(X)  # -1 = anomalie, 1 = normal
    features["is_anomaly"] = features["anomaly_score"] == -1

    return features


def main():
    print(f"[*] Lecture de : {INPUT_CSV}")
    if not INPUT_CSV.exists():
        print(f"[ERREUR] Fichier introuvable : {INPUT_CSV}")
        print("        Lance d'abord parse_logs.py pour générer ce fichier.")
        return

    df = load_data()
    print(f"[+] {len(df)} requêtes chargées.\n")

    features = build_features(df)
    print(f"[+] {len(features)} fenêtres de {TIME_BUCKET} avec du trafic.\n")
    print(features.to_string())

    results = detect_anomalies(features)

    anomalies = results[results["is_anomaly"]]
    print(f"\n[!] {len(anomalies)} fenêtre(s) anormale(s) détectée(s) :\n")
    if not anomalies.empty:
        print(anomalies[["request_count", "distinct_ips", "distinct_urls"]].to_string())
    else:
        print("Aucune anomalie détectée avec ce jeu de données.")

    results.to_csv(OUTPUT_CSV)
    print(f"\n[+] Résultats complets sauvegardés dans : {OUTPUT_CSV}")


if __name__ == "__main__":
    main()