# Interprète Instant (repo)

## `agent-cash.html` — interprétation sur téléphone (navigateur)

Page **statique** pour analyser une situation du moment :

- **Texte** libre, **URL** de contexte, **photo** (fichier ou caméra).
- **Dictée** (Web Speech API, surtout Chrome / Android) et **audio 5 s** → transcription via **OpenRouter Whisper** (`/v1/audio/transcriptions`) quand une clé est enregistrée.
- **Enrichissement Firecrawl** (optionnel) : scrape `https://…` saisi dans le champ URL ; peut échouer en **file://** ou sans CORS — prévoir Make/Telegram ou hébergement HTTPS.
- **Sortie structurée** : niveau d’urgence **vert / orange / rouge**, **action principale**, jusqu’à **3 conseils**, rappel secours si pertinent.
- **Historique** et clés stockés en **localStorage** (uniquement ce navigateur).

**Urgence réelle :** compose le **112** (ou les numéros locaux). Cet outil n’est pas un service de secours agréé.

### Clés API

- **OpenRouter** : [openrouter.ai/keys](https://openrouter.ai/keys) — obligatoire pour analyser / transcrire.
- **Firecrawl** : optionnel ; base API par défaut `https://api.firecrawl.dev` (modifiable dans l’interface).

### Ouvrir

Double-clic sur `agent-cash.html` ou ouvre-le depuis un petit serveur HTTP / hébergement statique pour de meilleurs résultats (micro, caméra, CORS).

---

## Automatisation 24/7 (Make + Telegram)

Voir **[`docs/blueprint-make-agent-cash.md`](docs/blueprint-make-agent-cash.md)** (prospection d’origine + **section 9** pour l’adaptation « Interprète instant »).

---

## Bot Telegram minimal (Python)

Dossier **`telegram_interpret_bot/`** : exemple avec clés en **variables d’environnement** uniquement. Voir son `README.md`.

---

## Ancienne version « prospection »

L’historique Git conserve les versions précédentes du fichier si tu dois retrouver l’UI Agent Cash / prospects.
