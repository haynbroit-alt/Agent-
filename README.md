# Agent Cash Ultra

Mini-application **100 % locale** (HTML + JavaScript) pour la prospection assistée par IA et la préparation de messages incluant offre et moyen de paiement.

## Utilisation

1. Ouvrez `agent-cash.html` dans un navigateur (double-clic ou « Ouvrir avec »).
2. Collez une [clé API OpenRouter](https://openrouter.ai/keys) et enregistrez-la (stockage dans le navigateur uniquement).
3. Renseignez votre offre, prix et RIB ou lien de paiement, puis utilisez la génération de prospects et de messages.

Les données (prospects, messages, clé) restent dans le **localStorage** de votre machine ; rien n’est envoyé à ce dépôt.

## Fichiers

- `agent-cash.html` — interface complète (styles + logique).

## Passer au mode « agent 24/7 » (Make + Telegram + Sheets)

Si tu veux quitter le stockage local pour un orchestrateur cloud, suis le plan détaillé (modules, colonnes Sheets, appels OpenRouter, branches Telegram) :

- **[`docs/blueprint-make-agent-cash.md`](docs/blueprint-make-agent-cash.md)** — blueprint Make.com sans secrets à coller dans le repo.
