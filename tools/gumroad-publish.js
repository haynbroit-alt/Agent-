#!/usr/bin/env node
/*
 * gumroad-publish.js — crée les produits Gumroad depuis products.json.
 *
 * SÉCURITÉ (important) :
 *  - Le token N'EST JAMAIS écrit dans ce fichier ni dans le repo.
 *  - Il est lu UNIQUEMENT depuis la variable d'environnement GUMROAD_ACCESS_TOKEN.
 *  - Ne colle jamais un token dans un chat, un commit ou un ticket. Si c'est arrivé,
 *    régénère-le dans Gumroad → Settings → Advanced → Applications.
 *
 * Usage :
 *   export GUMROAD_ACCESS_TOKEN="<ton_token_régénéré>"
 *   node tools/gumroad-publish.js verify      # lecture seule : vérifie le token/compte
 *   node tools/gumroad-publish.js list        # liste tes produits existants
 *   node tools/gumroad-publish.js create      # DRY-RUN : montre ce qui serait créé
 *   node tools/gumroad-publish.js create --publish   # crée réellement les produits
 *
 * Node 18+ requis (utilise fetch global). Aucune dépendance.
 */
"use strict";

const fs = require("fs");
const path = require("path");

const API = "https://api.gumroad.com/v2";

function die(msg) {
  console.error("\n✗ " + msg + "\n");
  process.exit(1);
}

// Lit le token au moment d'un appel API (pas au chargement) : le DRY-RUN marche sans token.
function requireToken() {
  const t = process.env.GUMROAD_ACCESS_TOKEN;
  if (!t) {
    die(
      "GUMROAD_ACCESS_TOKEN manquant.\n" +
        "  1. Régénère ton token dans Gumroad → Settings → Advanced → Applications.\n" +
        '  2. export GUMROAD_ACCESS_TOKEN="<ton_token>"\n' +
        "  3. relance la commande.\n" +
        "  (Ne colle jamais le token dans un fichier ou un chat.)"
    );
  }
  return t;
}

// Appel API générique. Le token passe en paramètre de formulaire (jamais loggué).
async function call(method, endpoint, params = {}) {
  const body = new URLSearchParams({ access_token: requireToken(), ...params });
  let res;
  if (method === "GET") {
    res = await fetch(`${API}${endpoint}?${body.toString()}`);
  } else {
    res = await fetch(`${API}${endpoint}`, {
      method,
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    });
  }
  let json;
  try {
    json = await res.json();
  } catch (e) {
    die(`Réponse non-JSON de l'API (HTTP ${res.status}). Vérifie le token / la connectivité.`);
  }
  return { ok: res.ok && json && json.success !== false, status: res.status, json };
}

async function verify() {
  const { ok, status, json } = await call("GET", "/user");
  if (!ok) die(`Vérification échouée (HTTP ${status}). Token invalide ou révoqué ? ${json && json.message ? json.message : ""}`);
  const u = json.user || {};
  console.log(`✓ Token valide. Connecté en tant que : ${u.name || u.email || u.user_id || "compte Gumroad"}`);
  return true;
}

async function list() {
  const { ok, status, json } = await call("GET", "/products");
  if (!ok) die(`Impossible de lister les produits (HTTP ${status}).`);
  const products = json.products || [];
  if (!products.length) {
    console.log("Aucun produit existant.");
    return;
  }
  console.log(`Produits existants (${products.length}) :`);
  for (const p of products) {
    const price = typeof p.price === "number" ? (p.price / 100).toFixed(2) : p.price;
    console.log(`  • ${p.name} — ${price} ${(p.currency || "").toUpperCase()}  [${p.published ? "publié" : "brouillon"}]`);
  }
}

function loadManifest() {
  const file = path.join(__dirname, "products.json");
  if (!fs.existsSync(file)) die("tools/products.json introuvable.");
  const data = JSON.parse(fs.readFileSync(file, "utf8"));
  if (!Array.isArray(data.products) || !data.products.length) die("products.json ne contient aucun produit.");
  return data;
}

async function create(publish) {
  const data = loadManifest();
  const currency = data.currency || "eur";

  if (!publish) {
    console.log("— DRY-RUN — (ajoute --publish pour créer réellement)\n");
    for (const p of data.products) {
      console.log(`  + ${p.name} — ${(p.price_cents / 100).toFixed(2)} ${currency.toUpperCase()}`);
    }
    console.log(`\n${data.products.length} produits seraient créés. Aucun appel d'écriture effectué.`);
    return;
  }

  // Mode réel : on vérifie le token d'abord.
  await verify();
  console.log("\nCréation des produits…\n");
  let created = 0;
  for (const p of data.products) {
    const { ok, status, json } = await call("POST", "/products", {
      name: p.name,
      price: String(p.price_cents),
      currency,
      description: p.description || "",
    });
    if (ok) {
      created++;
      const url = (json.product && (json.product.short_url || json.product.url)) || "";
      console.log(`  ✓ ${p.name} ${url ? "→ " + url : "(brouillon créé)"}`);
    } else {
      const msg = (json && json.message) || `HTTP ${status}`;
      console.log(`  ✗ ${p.name} — ${msg}`);
    }
  }
  console.log(`\nTerminé : ${created}/${data.products.length} créés.`);
  console.log("Ouvre ton tableau de bord Gumroad pour ajouter le fichier .zip, les visuels et publier chaque produit.");
}

(async function main() {
  const mode = process.argv[2];
  const publish = process.argv.includes("--publish");
  switch (mode) {
    case "verify": await verify(); break;
    case "list": await list(); break;
    case "create": await create(publish); break;
    default:
      console.log("Usage : node tools/gumroad-publish.js <verify|list|create> [--publish]");
      process.exit(mode ? 1 : 0);
  }
})().catch((e) => die(e && e.message ? e.message : String(e)));
