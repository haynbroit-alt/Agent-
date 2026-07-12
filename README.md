# Aurora — Premium Landing Page Kit

Un kit de site web **premium, 100 % statique et sans dépendance** (HTML + CSS + JS pur).
Conçu pour être **vendu comme produit numérique** (achat unique) : zéro serveur, zéro
abonnement à maintenir, zéro support technique lourd.

> Fait pour être mis en ligne une fois puis vendu en boucle sur Gumroad, Lemon Squeezy,
> Payhip ou ThemeForest.

## ✨ Ce qui est inclus

| Page | Fichier | Contenu |
|------|---------|---------|
| Accueil | `index.html` | Hero, logos, fonctionnalités, split features, stats, témoignages, FAQ, CTA |
| Tarifs | `pricing.html` | 3 plans, bascule mensuel/annuel, FAQ tarifs |
| À propos | `about.html` | Mission, stats, équipe, CTA recrutement |
| Blog | `blog.html` | Grille d'articles + inscription newsletter |
| Contact | `contact.html` | Formulaire complet + coordonnées |
| 404 | `404.html` | Page d'erreur soignée |

Plus :
- 🎨 **Mode clair / sombre** automatique (préférence système) + mémorisé, bouton de bascule.
- 📱 **100 % responsive** avec menu mobile.
- ⚡ **0 ko de dépendances JS** — un seul CSS, un seul JS léger.
- ♿ **Accessible** : HTML sémantique, focus visibles, `prefers-reduced-motion`.
- 🎛️ **Thème par variables CSS** : changez 3 couleurs, tout le site suit.
- ✅ Animations d'apparition au scroll, bascule de facturation, formulaires prêts.

## 🚀 Démarrer en 30 secondes

Aucune installation, aucun build. Ouvrez simplement le fichier :

```bash
# Option 1 — double-cliquez sur index.html

# Option 2 — petit serveur local (recommandé pour tester les liens)
python3 -m http.server 8000
# puis http://localhost:8000
```

## 📦 Structure

```
.
├── index.html          # Accueil
├── pricing.html        # Tarifs
├── about.html          # À propos
├── blog.html           # Blog
├── contact.html        # Contact
├── 404.html            # Erreur 404
├── assets/
│   ├── css/styles.css  # Tout le design system (variables en haut du fichier)
│   └── js/main.js      # Thème, menu mobile, scroll reveal, formulaires
├── CUSTOMIZING.md      # Guide de personnalisation
├── LICENSE.md          # Licence commerciale
└── SELLING.md          # Plan concret pour vendre ce kit
```

## 🎨 Personnalisation express

Tout se pilote depuis le haut de `assets/css/styles.css` :

```css
:root {
  --brand-1: #6d5efc;   /* couleur principale */
  --brand-2: #46c2ff;   /* couleur secondaire */
  --brand-3: #ff6ac1;   /* accent dégradé      */
}
```

Voir **[CUSTOMIZING.md](CUSTOMIZING.md)** pour le détail (logo, textes, formulaires, déploiement).

## 🌐 Déploiement (gratuit)

Ce site étant statique, il s'héberge gratuitement partout :

- **Netlify** : glissez-déposez le dossier sur app.netlify.com/drop
- **Vercel** : `vercel` dans le dossier
- **GitHub Pages** : poussez sur une branche `gh-pages`
- **Cloudflare Pages** : connectez le dépôt

## 💰 Le vendre

Ce dépôt **n'encaisse pas d'argent tout seul** — aucun code ne le peut. Le revenu vient
de vraies ventes sur une plateforme qui gère le paiement. Le plan complet, réaliste et
chiffré, est dans **[SELLING.md](SELLING.md)**.

## 📄 Licence

Voir **[LICENSE.md](LICENSE.md)**. Usage commercial autorisé pour vos projets et ceux de
vos clients ; la revente du template tel quel est interdite.
