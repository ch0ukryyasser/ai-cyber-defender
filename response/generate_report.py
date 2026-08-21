from fpdf import FPDF
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("response/incidents")
def _sanitize(text: str) -> str:
    """Remplace les caractères unicode non supportés par la police par défaut."""
    replacements = {
        "\u2019": "'", "\u2018": "'",   # apostrophes typographiques
        "\u201c": '"', "\u201d": '"',   # guillemets typographiques
        "\u2013": "-", "\u2014": "-",   # tirets longs
        "\u2026": "...",                 # points de suspension
        "🚨": "[!]",                     # emojis éventuels
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")

class IncidentReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Rapport d'incident - AI Cyber Defender", ln=True, align="C")
        self.ln(5)

def generate_report(ip: str, attack_type: str, details: str, blocked: bool) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = OUTPUT_DIR / f"incident_{ip.replace('.', '_')}_{timestamp}.pdf"

    pdf = IncidentReport()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Date : {datetime.now():%Y-%m-%d %H:%M:%S}", ln=True)
    pdf.cell(0, 10, f"IP source : {ip}", ln=True)
    pdf.cell(0, 10, f"Type d'attaque : {attack_type}", ln=True)
    pdf.cell(0, 10, f"Statut : {'Bloquée' if blocked else 'Non bloquée'}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, _sanitize(f"Détails :\n{details}"))

    pdf.output(str(filepath))
    print(f"[REPORT] Rapport généré : {filepath}")
    return filepath