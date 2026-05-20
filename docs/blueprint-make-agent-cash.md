# Blueprint Make.com — Agent autonome (Telegram + Sheets + OpenRouter)

Ce document prolonge **Agent Cash Ultra** (`agent-cash.html`) : même logique métier (prospects, génération, corrections), mais avec **Make.com** comme orchestrateur, **Google Sheets** comme base, et **Telegram** comme interface mobile. Aucune clé API ne doit figurer dans ce dépôt ni dans les scénarios exportés en clair : utilise les **connexions** et **variables** Make.

---

## 1. Architecture cible

| Composant | Rôle |
|-----------|------|
| **Telegram** | Commandes `/prospect`, `/campagne`, `/corriger` et notifications |
| **Make** | Déclencheurs, routage, appels HTTP, mise à jour Sheets |
| **OpenRouter** | Modèles type Claude Haiku / GPT-4.1 mini (facturation centralisée) |
| **Google Sheets** | Source de vérité : prospects, statuts, messages, corrections |
| **RSS / Apify** | Veille (signaux) → nouvelles lignes ou file « à qualifier » |

**Principe recommandé :** l’agent **prépare** les messages ; l’envoi sur les réseaux reste **manuel ou via un outil conforme** aux CGU, pour limiter risque juridique et bannissement de compte.

---

## 2. Google Sheets

### Feuille `Prospects`

| Colonne | Exemple | Notes |
|---------|---------|--------|
| `Id` | `abc12xyz` | Identifiant stable (Make : `{{uuid}}` ou concat timestamp) |
| `Nom` | Jean Dupont | |
| `Entreprise` | TechCorp | |
| `Besoin` | Automatiser la facturation | |
| `LinkedIn_URL` | https://… | Optionnel |
| `Email` | contact@… | Optionnel ; respect RGPD / base légale |
| `Statut` | `Attente` \| `Généré` \| `Envoyé_manuel` \| `Pause` | Filtré par `/campagne` |
| `Message_LinkedIn` | (texte) | Rempli après génération |
| `Message_Email` | (texte) | Idem |
| `Source` | `telegram` \| `reddit_rss` \| `apify` | Traçabilité |
| `Dernière_maj` | ISO datetime | |

### Feuille `Corrections`

| Colonne | Notes |
|---------|--------|
| `ProspectId` | Lien vers `Prospects.Id` |
| `Ancien_message` | Extrait du message remplacé |
| `Correction` | Texte validé |
| `Date` | |
| `Type_besoin` ou `Tag` | Pour filtrer les N dernières corrections « similaires » |

---

## 3. Scénario A — Telegram (commandes)

### Déclencheur

- **Telegram > Watch updates** (ou équivalent selon ton bot).

### Router sur le texte entrant

Normalise avec un module **Tools > Set variable** ou **Text parser** si besoin.

| Branche | Détection | Actions (ordre logique) |
|---------|-----------|-------------------------|
| **Ajout** | Commence par `/prospect` | Parser le corps : ex. `Jean\|TechCorp\|Besoin court` → **Google Sheets > Add a row** sur `Prospects` (`Statut = Attente`, `Source = telegram`) → **Telegram > Send a message** « Ligne créée : Id … » |
| **Campagne** | `/campagne` | **Search rows** `Statut = Attente` → **Iterator** sur chaque ligne → (optionnel) **Search rows** sur `Corrections` (5 dernières pour ce besoin ou global) → **HTTP > Make a request** OpenRouter → Parser JSON réponse → **Update a row** (`Message_*`, `Statut = Généré`, `Dernière_maj`) → **Telegram** envoi d’un résumé + textes (ou un message par prospect, selon ton confort) |
| **Correction** | `/corriger` | Parser `Id` + texte entre guillemets → **Add a row** `Corrections` → optionnel : **Update a row** sur prospect ou relancer une sous-branche « régénérer » |

### Appel OpenRouter (HTTP)

- **Method :** POST  
- **URL :** `https://openrouter.ai/api/v1/chat/completions`  
- **Headers :**  
  - `Authorization: Bearer <variable Make contenant la clé>`  
  - `Content-Type: application/json`  
  - Optionnel : `HTTP-Referer`, `X-Title` (recommandé par OpenRouter)

**Body (JSON) — exemple de structure :**

```json
{
  "model": "anthropic/claude-3-haiku",
  "messages": [
    {
      "role": "user",
      "content": "… prompt construit avec colonnes Sheets + bloc corrections …"
    }
  ],
  "max_tokens": 800,
  "temperature": 0.75
}
```

**Prompt (rappel métier) :** prospect, offre, prix, **lien de paiement** (Stripe / PayPal, pas RIB en clair dans les messages sortants si possible), style demandé, **réponses uniquement en JSON** avec clés `linkedin` et `email` (comme dans le HTML) pour faciliter le parse.

**Réponse :** extraire `choices[0].message.content` ; si le modèle entoure le JSON de fences ``` … ```, ajouter un module **Text > Replace** ou **Regex** pour les retirer avant **JSON > Parse JSON**.

### Gestion d’erreurs

- Sur **OpenRouter** ou **Sheets** : branche **error handler** → Telegram « Échec campagne ligne {{Id}} : {{erreur}} » pour ne pas perdre le fil en silence.

---

## 4. Scénario B — Veille (RSS ou webhook Apify)

### Déclencheur

- **RSS > Watch RSS feed items** sur une URL légale (flux public, ToS respectées), **ou**  
- **Webhooks > Custom webhook** recevant le payload Apify.

### Filtre

- Module **Filter** ou **Router** : mots-clés (`besoin`, `recommandation`, etc.).

### Sortie

- **Add a row** `Prospects` avec `Source`, lien du post, `Statut = À_qualifier` si les champs Nom/Entreprise sont vides ; **ou**  
- Passage par OpenRouter pour **structurer** le texte brut en JSON `{ nom, entreprise, besoin }` puis écriture Sheets.

**Réalisme :** beaucoup de signaux ne donnent pas d’email exploitable ; prévoir une **étape humaine** avant statut `Attente` plein pot.

---

## 5. Scénario C — Apprentissage

- Avant chaque génération dans la campagne : **Search rows** `Corrections`, tri par date décroissante, **limit 5** (Make : slice après agrégation ou requête côté Sheets avec une colonne d’index si besoin).  
- Concaténer dans le prompt : « Feedbacks précédents : … ».  
- Les corrections riches par **type de besoin** améliorent plus vite la qualité qu’un historique global uniquement.

---

## 6. Utilisation quotidienne (rappel)

1. Matin : `/campagne` → messages dans Telegram + mis à jour dans Sheets.  
2. Copier-coller vers LinkedIn / email **depuis Sheets ou Telegram** selon ce que tu as configuré.  
3. `/corriger` pour enregistrer une version meilleure.  
4. Soir : vérifier les alertes du scénario veille + lignes `À_qualifier`.

---

## 7. Import JSON Make

Les exports Make sont **liés au compte**, aux connexions OAuth et aux versions de modules : un fichier JSON copié d’ailleurs casse souvent à l’import. Ce blueprint est la **référence stable** à recâbler une fois ; ensuite tu peux **exporter** ton propre blueprint depuis Make pour sauvegarde privée (hors Git public, ou repo privé sans secrets).

---

## 8. Checklist conformité / risque

- [ ] Pas de clé dans les messages Telegram, les noms de scénarios ou les bundles Git.  
- [ ] CGU LinkedIn / X / Reddit : pas d’envoi massif automatisé non autorisé.  
- [ ] RGPD : base légale et mentions si données personnelles (emails, noms).  
- [ ] Paiement : liens Stripe/PayPal + facturation selon ton statut (auto-entrepreneur, société, etc.).

---

## Liens utiles

- [OpenRouter — clés API](https://openrouter.ai/keys)  
- [Documentation API chat completions OpenRouter](https://openrouter.ai/docs/api-reference/chat-completion)  
- Make : connexions **HTTP**, **Google Sheets**, **Telegram**

Pour revenir à la version locale sans orchestrateur : voir `agent-cash.html` et le `README.md` à la racine.
