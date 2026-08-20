"""Petit script pour lister les modèles Groq disponibles avec ta clé API."""
import os
from groq import Groq

client = Groq()
models = client.models.list()

print("Modèles disponibles sur ton compte Groq :\n")
for m in models.data:
    print(f"  - {m.id}")