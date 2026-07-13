# Templates de niche

Chaque sous-dossier est un **produit autonome** (HTML + CSS + JS, zéro dépendance), prêt à
vendre séparément ou en bundle. Voir `../MARKET-RESEARCH.md` pour le pourquoi et
`../PRODUCT-LINE.md` pour le packaging et la mise en vente.

| Dossier | Produit | Cible | Aperçu |
|---------|---------|-------|--------|
| `nova-ai/` | **Nova** | Startup / outil IA | Sombre, glow, waitlist, démo terminal |
| `mentor-coach/` | **Mentor** | Coach / créateur | Chaleureux, offres, témoignages, réservation |
| `onelink-bio/` | **Onelink** | Créateurs (link-in-bio) | Mobile-first, une page, liens + réseaux |
| `estate-realty/` | **Estate** | Agent / agence immobilière | Navy + or, recherche, listings, valuation |
| `bistro-restaurant/` | **Bistro** | Restaurant / commerce local | Chaleureux, menu, horaires, réservation |

## Démarrer

Aucun build. Ouvrez le `index.html` du dossier, ou lancez un serveur local :

```bash
python3 -m http.server 8000
# puis http://localhost:8000/templates/nova-ai/
```

## Personnaliser

- **Couleurs** : en haut de chaque `assets/style.css` (variables `--a1`, `--a2`, etc.).
- **Textes** : directement dans `index.html`.
- **Formulaires** : branchez votre service (Formspree, ConvertKit, Calendly…) — voir le
  commentaire `TODO` dans chaque `assets/app.js`.

## Déployer

Dossier statique → Netlify, Vercel, GitHub Pages, Cloudflare Pages. Gratuit chez la plupart.
