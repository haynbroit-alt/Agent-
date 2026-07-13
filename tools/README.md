# tools/ — automatisation de la mise en vente

Script pour créer tes produits sur Gumroad **via l'API**, au lieu de les saisir à la main.

## ⚠️ Sécurité — à lire avant tout

- **Ne colle jamais ton access token dans un chat, un fichier, un commit ou un ticket.**
  S'il a déjà été exposé (par ex. collé dans une conversation), **régénère-le** :
  Gumroad → **Settings → Advanced → Applications** → regénère le token.
- Le script lit le token **uniquement** depuis la variable d'environnement
  `GUMROAD_ACCESS_TOKEN`. Il n'est stocké nulle part dans le repo.
- Ne commit jamais le token. Ce dépôt n'en contient aucun.

## Prérequis

- Node 18+ (le script utilise `fetch` natif, aucune dépendance).
- Un token Gumroad **régénéré**, mis dans l'environnement :

```bash
export GUMROAD_ACCESS_TOKEN="<ton_token_régénéré>"
```

> Sur Claude Code on the web, ajoute plutôt le token dans les **secrets/variables
> d'environnement** de ton environnement, jamais en clair dans le chat.

## Utilisation

```bash
# 1) Vérifier que le token marche (lecture seule, aucun risque)
node tools/gumroad-publish.js verify

# 2) Voir tes produits existants
node tools/gumroad-publish.js list

# 3) Aperçu de ce qui serait créé (DRY-RUN, aucun appel d'écriture)
node tools/gumroad-publish.js create

# 4) Créer réellement les produits (après avoir relu products.json)
node tools/gumroad-publish.js create --publish
```

## Ce que ça fait / ne fait pas

- ✅ Crée les produits (nom, prix, description) depuis `products.json`.
- ❌ Ne **publie** pas automatiquement et n'uploade pas les fichiers : après création,
  va sur ton tableau de bord Gumroad pour ajouter le `.zip` de chaque template, les
  visuels, puis cliquer **Publish**. C'est volontaire — tu gardes le contrôle final.
- Si l'API refuse la création de produits sur ton compte/plan, le script affiche l'erreur
  et tu peux basculer sur la création manuelle (textes dans `../launch/gumroad-listings.md`).

## Personnaliser les produits

Édite `products.json` : noms, `price_cents` (en **centimes**), descriptions. Le manifeste
contient déjà les 6 templates + le bundle.
