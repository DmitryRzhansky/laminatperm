import { updateCartCount } from "./add-to-cart.js";

function formatRub(value) {
  const amount = Math.max(0, Math.round(Number(value) || 0));
  return `${amount.toLocaleString("ru-RU")} ₽`;
}

function parseUnitPrice(raw) {
  const value = Number(String(raw ?? "").replace(",", "."));
  return Number.isFinite(value) ? value : 0;
}

function normalizeQty(input) {
  const value = Math.max(0, Math.round(Number(String(input.value).replace(",", ".")) || 0));
  input.value = String(value);
  return value;
}

export function initCart() {
  const root = document.querySelector("[data-cart]");

  if (!root) {
    return;
  }

  const list = root.querySelector("[data-cart-list]");
  const totalNode = root.querySelector("[data-cart-total]");
  const timers = new WeakMap();

  const recalcTotals = () => {
    let total = 0;

    root.querySelectorAll("[data-cart-item]").forEach((item) => {
      const input = item.querySelector("[data-cart-qty-input]");
      const lineSum = item.querySelector("[data-cart-line-sum]");
      const unitPrice = parseUnitPrice(item.getAttribute("data-unit-price"));
      const quantity = normalizeQty(input);
      const sum = unitPrice * quantity;

      total += sum;

      if (lineSum) {
        lineSum.textContent = formatRub(sum);
      }
    });

    if (totalNode) {
      totalNode.textContent = formatRub(total);
    }
  };

  const persist = async (item) => {
    const form = item.querySelector("[data-cart-form]");
    const input = item.querySelector("[data-cart-qty-input]");

    if (!form || !input) {
      return;
    }

    const quantity = normalizeQty(input);
    const body = new FormData(form);
    body.set("quantity", String(quantity));

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
        throw new Error(`Cart update failed: ${response.status}`);
      }

      const data = await response.json();

      if (data.removed) {
        item.remove();
      }

      if (typeof data.cart_count === "number") {
        updateCartCount(data.cart_count);
      }

      if (totalNode && typeof data.total_formatted === "string") {
        totalNode.textContent = data.total_formatted;
      } else {
        recalcTotals();
      }

      if (!list?.querySelector("[data-cart-item]")) {
        window.location.reload();
      }
    } catch (error) {
      console.error("[laminatperm] cart update failed:", error);
      form.submit();
    }
  };

  const schedulePersist = (item) => {
    const previous = timers.get(item);

    if (previous) {
      window.clearTimeout(previous);
    }

    timers.set(
      item,
      window.setTimeout(() => {
        persist(item);
      }, 280),
    );
  };

  root.querySelectorAll("[data-cart-item]").forEach((item) => {
    const form = item.querySelector("[data-cart-form]");
    const input = item.querySelector("[data-cart-qty-input]");

    if (!form || !input) {
      return;
    }

    item.querySelectorAll("[data-cart-qty]").forEach((button) => {
      button.addEventListener("click", () => {
        const delta = Number(button.getAttribute("data-cart-qty")) || 0;
        input.value = String(Math.max(0, normalizeQty(input) + delta));
        recalcTotals();
        schedulePersist(item);
      });
    });

    input.addEventListener("input", () => {
      recalcTotals();
      schedulePersist(item);
    });

    input.addEventListener("change", () => {
      normalizeQty(input);
      recalcTotals();
      schedulePersist(item);
    });

    input.addEventListener("blur", () => {
      normalizeQty(input);
      recalcTotals();
    });

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      normalizeQty(input);
      recalcTotals();
      persist(item);
    });

    const remove = item.querySelector("[data-cart-remove]");

    if (remove) {
      remove.addEventListener("click", () => {
        input.value = "0";
        recalcTotals();
        persist(item);
      });
    }
  });

  recalcTotals();
}
