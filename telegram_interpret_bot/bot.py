"""
Minimal Telegram bot: text in -> OpenRouter interpret JSON -> readable reply.
Configure env TELEGRAM_BOT_TOKEN and OPENROUTER_API_KEY. No secrets in code.
"""
from __future__ import annotations

import json
import os
import re

import httpx
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_INTERPRET = """Tu es un assistant d'interprétation de situation immédiate (sécurité, prudence, orientation).
Règles strictes :
1. Ne donne jamais d'instructions illégales ou dangereuses.
2. Ne remplace jamais un avis médical, juridique, ni les services de secours. Urgence vitale : oriente vers le 112 (Europe) ou les numéros locaux.
3. Ne prescrit jamais de médicament, dose, posologie, ni diagnostic médical.
4. Ne prends pas de décisions financières à la place de l'utilisateur.
5. Si tu manques d'informations fiables, dis-le clairement.
6. Reste factuel, prudent, et légal.

Réponds UNIQUEMENT en JSON valide (sans markdown) avec cette forme exacte :
{"urgence":"vert|orange|rouge","action_principale":"une phrase courte","conseils":["c1","c2","c3"],"rappel_secours":"phrase ou chaîne vide"}
"""


def strip_json_fence(text: str) -> str:
    text = text.strip()
    m = re.match(r"^```(?:json)?\s*([\s\S]*?)\s*```$", text, re.I)
    return m.group(1).strip() if m else text


def format_parsed(o: dict) -> str:
    u = (o.get("urgence") or "orange").lower()
    label = {"rouge": "🔴 Urgence élevée", "orange": "🟠 Prudence", "vert": "🟢 Info / calme"}.get(u, "🟠 Prudence")
    lines = [label, "", "▶ " + str(o.get("action_principale") or "").strip()]
    cons = o.get("conseils") or []
    if isinstance(cons, list) and cons:
        lines.append("")
        for i, c in enumerate(cons[:3], 1):
            lines.append(f"{i}. {c}")
    rs = str(o.get("rappel_secours") or "").strip()
    if rs:
        lines.extend(["", "⚠️ " + rs])
    return "\n".join(lines)


async def openrouter_interpret(user_text: str) -> str:
    model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
    key = os.environ["OPENROUTER_API_KEY"]
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_INTERPRET},
            {"role": "user", "content": user_text},
        ],
        "max_tokens": 900,
        "temperature": 0.35,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/local/telegram_interpret_bot",
        "X-Title": "Telegram Interpret Bot",
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(OPENROUTER_URL, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
    raw = data["choices"][0]["message"]["content"] or ""
    try:
        obj = json.loads(strip_json_fence(raw))
        if not isinstance(obj, dict):
            raise ValueError("not an object")
        return format_parsed(obj)
    except (json.JSONDecodeError, ValueError, KeyError):
        return raw[:4000] if raw else "Réponse vide."


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    if not text:
        return
    try:
        out = await openrouter_interpret(text)
        await update.message.reply_text(out[:4096])
    except Exception as e:  # noqa: BLE001 — show user a short error
        await update.message.reply_text(f"Erreur : {e!s}"[:1024])


def main() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
