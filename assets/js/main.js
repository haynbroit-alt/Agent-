/* ==========================================================================
   Aurora — interactions. Vanilla JS, no dependencies.
   ========================================================================== */
(function () {
  "use strict";

  /* ---- Theme (persisted, respects OS preference) ------------------------ */
  var root = document.documentElement;
  var stored = null;
  try { stored = localStorage.getItem("aurora-theme"); } catch (e) {}
  var prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  root.setAttribute("data-theme", stored || (prefersDark ? "dark" : "light"));

  function toggleTheme() {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("aurora-theme", next); } catch (e) {}
  }

  /* ---- Wire up after DOM ready ------------------------------------------ */
  document.addEventListener("DOMContentLoaded", function () {
    // Theme toggle button(s)
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.addEventListener("click", toggleTheme);
    });

    // Mobile nav
    var nav = document.querySelector(".nav");
    var navToggle = document.querySelector(".nav-toggle");
    if (nav && navToggle) {
      navToggle.addEventListener("click", function () {
        var open = nav.classList.toggle("open");
        navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      });
      nav.querySelectorAll(".nav-links a").forEach(function (a) {
        a.addEventListener("click", function () { nav.classList.remove("open"); });
      });
    }

    // Scroll reveal
    var reveals = document.querySelectorAll(".reveal");
    if ("IntersectionObserver" in window && reveals.length) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) { entry.target.classList.add("in"); io.unobserve(entry.target); }
        });
      }, { threshold: 0.12 });
      reveals.forEach(function (el) { io.observe(el); });
    } else {
      reveals.forEach(function (el) { el.classList.add("in"); });
    }

    // Pricing billing toggle (monthly / yearly)
    var billing = document.querySelector("[data-billing-toggle]");
    if (billing) {
      billing.addEventListener("change", function () {
        var yearly = billing.checked;
        document.querySelectorAll("[data-price-monthly]").forEach(function (el) {
          var amount = yearly ? el.getAttribute("data-price-yearly") : el.getAttribute("data-price-monthly");
          var period = el.querySelector("span");
          el.childNodes[0].nodeValue = amount;
          if (period) period.textContent = yearly ? "/an" : "/mois";
        });
      });
    }

    // Contact / newsletter forms — client-side demo handling.
    // Replace the handler with your own endpoint (Formspree, Netlify Forms, etc.).
    document.querySelectorAll("[data-demo-form]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (!form.checkValidity()) { form.reportValidity(); return; }
        var ok = form.querySelector(".form-success");
        if (ok) { ok.classList.add("show"); }
        form.reset();
      });
    });

    // Footer year
    var y = document.querySelector("[data-year]");
    if (y) y.textContent = new Date().getFullYear();
  });
})();
