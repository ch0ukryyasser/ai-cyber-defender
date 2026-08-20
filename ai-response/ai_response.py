"""
AI Cyber Defender - Phase 3 : Intégration IA générative / Agent (version Groq - 100% gratuit)
================================================================================================

Ce module reçoit une alerte détectée en Phase 2 (IP suspecte, pattern
d'attaque, extrait de logs) et utilise l'API Groq (modèles open-source
comme Llama 3.3, gratuite) pour :

  1. Analyser le contexte et produire une sortie JSON structurée
     (type d'attaque, gravité, explication, action recommandée).
  2. (Niveau agent) Laisser le LLM décider d'appeler des outils :
     block_ip(), send_alert(), create_ticket().

Prérequis :
    pip install groq
    variable d'environnement GROQ_API_KEY définie
    (clé gratuite sur https://console.groq.com/keys)

Usage rapide :
    python ai_response.py
"""

import json
import os
from groq import Groq

# ---------------------------------------------------------------------------
# Client Groq
# ---------------------------------------------------------------------------

client = Groq()  # lit automatiquement GROQ_API_KEY dans l'environnement

# Modèle open-source gratuit, bon compromis qualité/vitesse/support JSON+tools
# (liste à jour vérifiable avec list_models.py si Groq change encore son catalogue)
MODEL = "openai/gpt-oss-120b"


# ---------------------------------------------------------------------------
# ÉTAPE 1-3 : Analyse simple avec sortie JSON forcée
# ---------------------------------------------------------------------------

ANALYSIS_SYSTEM_PROMPT = """Tu es un analyste SOC (Security Operations Center) expert.
Tu reçois le contexte d'une alerte de sécurité détectée automatiquement
(IP source, pattern détecté, extrait de logs bruts).

Ta tâche : analyser cette alerte et répondre UNIQUEMENT avec un objet JSON valide,
respectant EXACTEMENT ce schéma :

{
  "attack_type": "<type d'attaque probable, ex: SQL Injection, Brute Force, XSS, Port Scan, etc.>",
  "severity": "<low|medium|high|critical>",
  "confidence": <nombre entre 0 et 100>,
  "explanation": "<explication claire en 2-3 phrases, compréhensible par un humain non-expert>",
  "recommended_action": "<action recommandée concrète, ex: bloquer l'IP, surveiller, ignorer (faux positif probable), escalader>"
}

Règles :
- Base-toi uniquement sur les preuves fournies (logs, IP, pattern).
- Si les preuves sont insuffisantes, mets confidence bas et severity "low".
- Ne jamais inventer d'informations qui ne sont pas dans le contexte fourni."""


def analyze_alert_simple(alert: dict) -> dict:
    """
    Envoie une alerte au LLM (Groq/Llama) et récupère une analyse structurée en JSON.

    alert doit contenir au minimum :
        - source_ip (str)
        - pattern_detected (str)  -> ex: "SQLi payload in query string"
        - log_excerpt (str)       -> quelques lignes de access.log pertinentes
        - timestamp (str, optionnel)

    Retourne un dict Python avec les clés :
        attack_type, severity, confidence, explanation, recommended_action
    """
    user_context = f"""Voici le contexte de l'alerte détectée :

IP source        : {alert.get('source_ip', 'inconnue')}
Timestamp         : {alert.get('timestamp', 'inconnu')}
Pattern détecté   : {alert.get('pattern_detected', 'non spécifié')}
Extrait de logs   :
{alert.get('log_excerpt', '(aucun log fourni)')}

Analyse cette alerte et réponds selon le format JSON demandé."""

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=1024,
        response_format={"type": "json_object"},  # force une sortie JSON valide côté Groq
        messages=[
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_context},
        ],
    )

    raw_text = response.choices[0].message.content.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        return {
            "error": f"JSON invalide renvoyé par le modèle: {e}",
            "raw_response": raw_text,
        }


# ---------------------------------------------------------------------------
# ÉTAPE 4 : Niveau agent - le LLM peut appeler des outils
# ---------------------------------------------------------------------------

# --- Implémentations des outils (stubs pour l'instant) ---------------------
# À terme : block_ip() appellera ton pare-feu / iptables / règle Docker,
# send_alert() enverra un mail/Slack/webhook, create_ticket() créera un
# ticket Jira/GitHub Issue. Pour l'instant on log dans la console pour
# valider la logique de l'agent.

def block_ip(ip: str, reason: str) -> str:
    print(f"[ACTION] block_ip appelé -> IP={ip} | raison: {reason}")
    # TODO Phase 4/5 : intégrer un vrai blocage (iptables, règle Docker, WAF...)
    return f"IP {ip} bloquée avec succès (simulation)."


def send_alert(message: str, severity: str) -> str:
    print(f"[ACTION] send_alert appelé -> [{severity.upper()}] {message}")
    # TODO Phase 4/5 : intégrer Slack webhook / email / SMS
    return "Alerte envoyée avec succès (simulation)."


def create_ticket(title: str, description: str, priority: str) -> str:
    print(f"[ACTION] create_ticket appelé -> [{priority}] {title}\n         {description}")
    # TODO Phase 4/5 : intégrer GitHub Issues API ou Jira
    return "Ticket créé avec succès (simulation), ID=TICKET-0001."


TOOL_IMPLEMENTATIONS = {
    "block_ip": block_ip,
    "send_alert": send_alert,
    "create_ticket": create_ticket,
}

# --- Définition des outils au format OpenAI-compatible (attendu par Groq) --

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "block_ip",
            "description": "Bloque une adresse IP identifiée comme malveillante. À utiliser uniquement pour les attaques confirmées avec un niveau de confiance élevé.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ip": {"type": "string", "description": "Adresse IP à bloquer"},
                    "reason": {"type": "string", "description": "Raison du blocage"},
                },
                "required": ["ip", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_alert",
            "description": "Envoie une alerte à l'équipe de sécurité (Slack/email). À utiliser pour prévenir un humain d'une menace détectée.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Contenu de l'alerte"},
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                    },
                },
                "required": ["message", "severity"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Crée un ticket de suivi pour une investigation approfondie ou une action différée.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                },
                "required": ["title", "description", "priority"],
            },
        },
    },
]

AGENT_SYSTEM_PROMPT = """Tu es un agent IA de réponse à incident pour une plateforme de détection
d'attaques web (AI Cyber Defender). Tu reçois le contexte d'une alerte de sécurité.

Ton rôle :
1. Analyser la menace.
2. Décider, selon la gravité, quels outils appeler parmi : block_ip, send_alert, create_ticket.
   - critical/high + confiance élevée -> bloque l'IP ET envoie une alerte.
   - medium -> envoie une alerte et/ou crée un ticket pour investigation.
   - low -> crée un ticket seulement, ou ne fais rien si c'est clairement un faux positif.
3. Explique brièvement ton raisonnement en texte avant d'appeler les outils.

N'appelle JAMAIS block_ip si tu n'es pas raisonnablement confiant qu'il s'agit d'une vraie attaque :
un faux blocage peut couper l'accès à un utilisateur légitime."""


def analyze_alert_agent(alert: dict, max_turns: int = 5) -> dict:
    """
    Version agent : le LLM peut décider d'appeler block_ip / send_alert /
    create_ticket. On boucle tant qu'il demande des tool_calls, et on exécute
    réellement les fonctions Python correspondantes.

    Retourne un résumé : le texte final du modèle + la liste des actions exécutées.
    """
    user_context = f"""Alerte détectée :

IP source        : {alert.get('source_ip', 'inconnue')}
Timestamp         : {alert.get('timestamp', 'inconnu')}
Pattern détecté   : {alert.get('pattern_detected', 'non spécifié')}
Extrait de logs   :
{alert.get('log_excerpt', '(aucun log fourni)')}

Analyse cette alerte et prends les actions appropriées."""

    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_context},
    ]
    actions_taken = []
    final_text = ""

    for _ in range(max_turns):
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            tool_choice="auto",
            messages=messages,
        )

        msg = response.choices[0].message

        if msg.content:
            final_text += msg.content + "\n"

        if not msg.tool_calls:
            break  # le modèle a fini, pas d'autre outil à appeler

        # Le modèle veut appeler un ou plusieurs outils : on les exécute
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": msg.tool_calls,
        })

        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)

            fn = TOOL_IMPLEMENTATIONS.get(fn_name)
            if fn is None:
                result_text = f"Outil inconnu: {fn_name}"
            else:
                result_text = fn(**fn_args)
                actions_taken.append({"tool": fn_name, "input": fn_args, "result": result_text})

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": fn_name,
                "content": str(result_text),
            })

    return {
        "reasoning": final_text.strip(),
        "actions_taken": actions_taken,
    }


# ---------------------------------------------------------------------------
# Test rapide
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        print("GROQ_API_KEY n'est pas définie. Configure-la avant de lancer ce script.")
        raise SystemExit(1)

    # Exemple d'alerte -> adapte les clés à ce que ton script Phase 2 produit réellement
    sample_alert = {
        "source_ip": "203.0.113.42",
        "timestamp": "2026-08-19T14:32:10Z",
        "pattern_detected": "Tentatives de SQLi répétées (payload ' OR '1'='1 détecté 15 fois en 30s)",
        "log_excerpt": (
            '203.0.113.42 - - [19/Aug/2026:14:32:05] "GET /login?user=admin\'--%20 HTTP/1.1" 401\n'
            '203.0.113.42 - - [19/Aug/2026:14:32:06] "GET /login?user=\' OR \'1\'=\'1 HTTP/1.1" 401\n'
            '203.0.113.42 - - [19/Aug/2026:14:32:07] "GET /login?user=1; DROP TABLE users;-- HTTP/1.1" 401'
        ),
    }

    print("=" * 70)
    print("TEST 1 : Analyse simple (JSON structuré)")
    print("=" * 70)
    result_simple = analyze_alert_simple(sample_alert)
    print(json.dumps(result_simple, indent=2, ensure_ascii=False))

    print()
    print("=" * 70)
    print("TEST 2 : Niveau agent (avec outils)")
    print("=" * 70)
    result_agent = analyze_alert_agent(sample_alert)
    print("\nRaisonnement du modèle:")
    print(result_agent["reasoning"])
    print("\nActions exécutées:")
    for action in result_agent["actions_taken"]:
        print(f"  - {action['tool']}({action['input']}) -> {action['result']}")