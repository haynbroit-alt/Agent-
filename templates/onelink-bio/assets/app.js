/* Onelink — minimal interactions. Replace form handler with your endpoint. */
(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-form]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (!form.checkValidity()) { form.reportValidity(); return; }
        var ok = document.querySelector("[data-ok]");
        if (ok) ok.classList.add("show");
        form.reset();
        // TODO: connect the email to Mailchimp / ConvertKit / Formspree.
      });
    });
  });
})();
