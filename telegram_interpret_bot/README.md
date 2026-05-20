# Bot Telegram minimal — Interprétation (OpenRouter)

Petit exemple **serveur** : les utilisateurs envoient un **message texte** au bot ; le bot appelle **OpenRouter** avec le même type de consignes que `agent-cash.html` (sécurité, pas de posologie, orientation secours).

## Prérequis

- Python 3.10+
- Un bot Telegram ([@BotFather](https://t.me/BotFather)) → token
- Une clé [OpenRouter](https://openrouter.ai/keys)

## Installation

```bash
cd telegram_interpret_bot
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

```bash
export TELEGRAM_BOT_TOKEN="…"
export OPENROUTER_API_KEY="sk-or-v1-…"
# optionnel :
export OPENROUTER_MODEL="google/gemini-2.0-flash-001"
```

## Lancer

```bash
python bot.py
```

## Limites de cet exemple

- Gère surtout le **texte**. Pour **photos** et **vocaux**, branche le téléchargement des fichiers Telegram puis multimodal / Whisper (voir `docs/blueprint-make-agent-cash.md` section 9).
- Pas de stockage persistant (pas de Sheets) : à ajouter si tu veux un historique partagé.
