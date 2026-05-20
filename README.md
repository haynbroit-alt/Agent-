# Interprète Instant (repo)

## `agent-cash.html` — interprétation sur téléphone (navigateur)

Page **statique** pour analyser une situation du moment :

- **Texte** libre, **URL** de contexte (même sans Firecrawl : l’URL est transmise au modèle), **photo** (fichier ou caméra) avec **redimensionnement** avant envoi et limite de taille.
- **Dictée** (Web Speech API, surtout Chrome / Android) et **audio 5 s** → transcription via **OpenRouter Whisper** ; choix automatique **WebM / MP4** selon le navigateur.
- **Enrichissement Firecrawl** (optionnel) : scrape `https://…` ; messages d’erreur plus clairs ; peut échouer en **file://** (CORS) — prévoir HTTPS ou Make/Telegram.
- **Sortie structurée** : urgence **vert / orange / rouge**, **action principale**, jusqu’à **3 conseils** ; parsing JSON **tolérant** (fences markdown, texte autour du JSON).
- **UX** : panneau réglages repliable, **Ctrl+Entrée** pour lancer l’analyse, anti double-clic pendant l’appel API, toasts d’erreur distincts, **historique** cliquable pour recharger le texte, confirmation avant effacement total.
- **Accessibilité** : `aria-live` sur le résultat, libellés `for`/`id`, focus visible, zones tactiles élargies.
- **Historique** et clés en **localStorage** ; bouton pour **effacer la clé** OpenRouter du navigateur ; **modèle mémorisé** entre sessions.

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
