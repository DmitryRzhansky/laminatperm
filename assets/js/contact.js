(function initContactForm() {
  function formatPhone(value) {
    const digits = value.replace(/\D/g, "");

    let normalized = digits;
    if (normalized.startsWith("8")) {
      normalized = `7${normalized.slice(1)}`;
    }
    if (!normalized.startsWith("7")) {
      normalized = `7${normalized}`;
    }

    normalized = normalized.slice(0, 11);
    const local = normalized.slice(1);

    let formatted = "+7";
    if (local.length > 0) {
      formatted += ` (${local.slice(0, 3)}`;
    }
    if (local.length >= 3) {
      formatted += `) ${local.slice(3, 6)}`;
    }
    if (local.length >= 6) {
      formatted += `-${local.slice(6, 8)}`;
    }
    if (local.length >= 8) {
      formatted += `-${local.slice(8, 10)}`;
    }

    return formatted;
  }

  function clearFieldError(field) {
    field.removeAttribute("aria-invalid");
    const error = field.parentElement?.querySelector("[data-field-error]");
    if (error) {
      error.hidden = true;
      error.textContent = "";
    }
  }

  function setFieldError(field, message) {
    field.setAttribute("aria-invalid", "true");
    const error = field.parentElement?.querySelector("[data-field-error]");
    if (error) {
      error.hidden = false;
      error.textContent = message;
    }
  }

  function initPhoneMask(form) {
    const input = form.querySelector('input[name="phone"]');

    if (!(input instanceof HTMLInputElement)) {
      return;
    }

    input.addEventListener("input", () => {
      input.value = formatPhone(input.value);
    });

    input.addEventListener("focus", () => {
      if (!input.value) {
        input.value = "+7 (";
      }
    });

    input.addEventListener("blur", () => {
      if (input.value === "+7 (" || input.value === "+7") {
        input.value = "";
      }
    });
  }

  function validateForm(form) {
    const requiredFields = Array.from(
      form.querySelectorAll("[data-required]")
    );
    let isValid = true;
    const messages = [];

    requiredFields.forEach((field) => {
      clearFieldError(field);

      const value = field.value.trim();
      const label = field.getAttribute("data-label") || "Поле";

      if (!value || (field.tagName === "SELECT" && value === "")) {
        setFieldError(field, "Заполните поле");
        messages.push(`${label}: заполните поле`);
        isValid = false;
        return;
      }

      if (field.name === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        setFieldError(field, "Укажите корректный email");
        messages.push(`${label}: укажите корректный email`);
        isValid = false;
      }

      if (field.name === "phone") {
        const digits = value.replace(/\D/g, "");
        if (digits.length !== 11) {
          setFieldError(field, "Укажите телефон полностью");
          messages.push(`${label}: укажите телефон полностью`);
          isValid = false;
        }
      }
    });

    const consent = form.querySelector('input[name="consent"]');
    if (consent instanceof HTMLInputElement && !consent.checked) {
      messages.push("Нужно согласие на обработку персональных данных");
      isValid = false;
    }

    return { isValid, messages };
  }

  function init() {
    const form = document.querySelector("[data-request-form]");

    if (!form || form.dataset.contactReady === "true") {
      return;
    }

    form.dataset.contactReady = "true";
    initPhoneMask(form);

    const summary = form.querySelector("[data-form-error-summary]");
    const success = form.querySelector("[data-form-success]");

    form.querySelectorAll("[data-required]").forEach((field) => {
      field.addEventListener("input", () => clearFieldError(field));
      field.addEventListener("change", () => clearFieldError(field));
    });

    form.addEventListener("submit", (event) => {
      event.preventDefault();

      if (success) {
        success.hidden = true;
      }

      const honeypot = form.querySelector('input[name="website"]');
      if (honeypot instanceof HTMLInputElement && honeypot.value.trim()) {
        return;
      }

      const { isValid, messages } = validateForm(form);

      if (!isValid) {
        if (summary) {
          summary.hidden = false;
          summary.textContent = messages[0] || "Проверьте поля формы";
          summary.focus();
        }
        return;
      }

      if (summary) {
        summary.hidden = true;
      }

      if (success) {
        success.hidden = false;
        success.focus();
      }

      form.reset();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
