# Guide de personnalisation

Aucune compétence avancée requise — des bases en HTML/CSS suffisent.

## 1. Les couleurs (le plus rapide)

Ouvrez `assets/css/styles.css`. Tout en haut, dans `:root` :

```css
--brand-1: #6d5efc;   /* principale : boutons, liens, accents */
--brand-2: #46c2ff;   /* secondaire : milieu du dégradé */
--brand-3: #ff6ac1;   /* accent : fin du dégradé */
```

Changez ces trois valeurs et **tout le site** (boutons, dégradés, icônes, hero) suit.

Pour ajuster le thème sombre, modifiez le bloc `:root[data-theme="dark"]` juste en dessous.

## 2. Le nom / logo

Le logo est du texte + un carré dégradé (`.brand-mark`). Cherchez `Aurora` dans les fichiers
HTML et remplacez par votre nom. Pour un vrai logo image :

```html
<a class="brand" href="index.html">
  <img src="assets/img/logo.svg" alt="Mon produit" height="28" />
</a>
```

Le favicon est un SVG inline dans chaque `<head>` (attribut `rel="icon"`). Remplacez-le par
votre propre fichier si besoin.

## 3. Les textes

Tous les textes sont directement dans les fichiers `.html`. Ouvrez chaque page et modifiez
le contenu entre les balises. Rien n'est généré dynamiquement.

## 4. La typographie

Par défaut on utilise la police système (rapide, zéro requête). Pour une police web,
ajoutez dans le `<head>` de chaque page votre `<link>` de police puis, dans `styles.css` :

```css
:root { --font: "Inter", -apple-system, sans-serif; }
```

## 5. Les formulaires (contact & newsletter)

Par défaut les formulaires affichent un message de succès **sans rien envoyer** (démo).
Pour recevoir réellement les messages, branchez un service sans back-end :

- **Formspree** : `<form action="https://formspree.io/f/VOTRE_ID" method="POST">`
- **Netlify Forms** : ajoutez `netlify` à la balise `<form>` si vous hébergez sur Netlify.

Puis retirez l'attribut `data-demo-form` de la balise `<form>` pour laisser l'envoi réel se faire.

## 6. Les tarifs

Dans `pricing.html`, chaque prix est piloté par deux attributs pour la bascule mensuel/annuel :

```html
<div class="amount" data-price-monthly="19€" data-price-yearly="15€">19€<span>/mois</span></div>
```

Modifiez les montants et le contenu des listes `<ul>` de chaque plan.

## 7. Ajouter / retirer une section

Chaque section est un bloc `<section>…</section>` indépendant. Copiez-collez, réordonnez
ou supprimez librement. La classe `.reveal` déclenche l'animation d'apparition au scroll.

## 8. Déployer

Voir la section « Déploiement » du `README.md`. En résumé : c'est un dossier de fichiers,
déposez-le sur n'importe quel hébergeur statique.
