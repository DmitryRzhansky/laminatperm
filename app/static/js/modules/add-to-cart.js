function updateCartCount(count) {
  const value = Math.max(0, Number(count) || 0);
  const label = value > 0 ? `Корзина: ${value}` : "Корзина";

  document.querySelectorAll("[data-cart-count]").forEach((node) => {
    node.textContent = value > 0 ? `(${value})` : "0";
    node.hidden = value <= 0;
    node.classList.toggle("is-empty", value <= 0);
  });

  document.querySelectorAll("[data-cart-link]").forEach((link) => {
    link.setAttribute("aria-label", label);
    link.classList.toggle("has-items", value > 0);
  });
}

function getSubmitButton(form) {
  return form.querySelector("[data-add-to-cart-btn]") || form.querySelector('button[type="submit"]');
}

function setBusy(form, busy) {
  const button = getSubmitButton(form);

  form.classList.toggle("is-busy", busy);

  if (button) {
    button.disabled = busy;
  }
}

function showAddedState(form) {
  const button = getSubmitButton(form);
  const defaultState = form.querySelector("[data-add-to-cart-default]");
  const successState = form.querySelector("[data-add-to-cart-success]");

  form.classList.add("is-added");

  if (defaultState) {
    defaultState.hidden = true;
  }

  if (successState) {
    successState.hidden = false;
  }

  if (button) {
    button.setAttribute("aria-live", "polite");
  }

  const previousTimer = form._addedTimer;

  if (previousTimer) {
    window.clearTimeout(previousTimer);
  }

  form._addedTimer = window.setTimeout(() => {
    form.classList.remove("is-added");

    if (defaultState) {
      defaultState.hidden = false;
    }

    if (successState) {
      successState.hidden = true;
    }

    form._addedTimer = null;
  }, 1800);
}

async function submitAddToCart(form) {
  if (form.classList.contains("is-busy")) {
    return null;
  }

  const body = new FormData(form);

  setBusy(form, true);

  try {
    const response = await fetch(form.action, {
      method: "POST",
      body,
      headers: {
        Accept: "application/json",
        "X-Requested-With": "fetch",
      },
      credentials: "same-origin",
    });

    if (!response.ok) {
      throw new Error(`Add to cart failed: ${response.status}`);
    }

    const data = await response.json();

    if (typeof data.cart_count === "number") {
      updateCartCount(data.cart_count);
    }

    showAddedState(form);
    return data;
  } catch (error) {
    console.error("[laminatperm] add to cart failed:", error);
    form.submit();
    return null;
  } finally {
    setBusy(form, false);
  }
}

export function initAddToCart() {
  document.querySelectorAll("[data-add-to-cart]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      submitAddToCart(form);
    });
  });
}

export { updateCartCount };
