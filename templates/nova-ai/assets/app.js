/* Nova — minimal interactions. Replace form handler with your endpoint. */
(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", function () {
    var y = document.querySelector("[data-year]");
    if (y) y.textContent = new Date().getFullYear();

    document.querySelectorAll("[data-form]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (!form.checkValidity()) { form.reportValidity(); return; }
        var ok = document.querySelector("[data-ok]");
        if (ok) ok.classList.add("show");
        form.reset();
        // TODO: POST the email to your service (Formspree, ConvertKit, Mailchimp…).
      });
    });
  });
})();
