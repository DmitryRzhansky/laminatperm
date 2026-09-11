export function initProductPage() {
  const root = document.querySelector("[data-product]");

  if (!root) {
    return;
  }

  initGallery(root);
  initTabs(root);
  initQuantity(root);
}

function initQuantity(root) {
  const form = root.querySelector("[data-product-cart]");
  const input = root.querySelector("[data-product-qty-input]");

  if (!form || !input) {
    return;
  }

  const normalize = () => {
    const value = Math.max(1, Math.round(Number(input.value) || 1));
    input.value = String(value);
    return value;
  };

  root.querySelectorAll("[data-product-qty]").forEach((button) => {
    button.addEventListener("click", () => {
      const delta = Number(button.getAttribute("data-product-qty")) || 0;
      input.value = String(Math.max(1, normalize() + delta));
    });
  });

  input.addEventListener("change", normalize);
  input.addEventListener("blur", normalize);
  form.addEventListener("submit", normalize);
}

function initGallery(root) {
  const main = root.querySelector("[data-product-main]");
  const thumbs = Array.from(root.querySelectorAll("[data-product-thumb]"));

  if (!main || thumbs.length === 0) {
    return;
  }

  thumbs.forEach((thumb) => {
    thumb.addEventListener("click", () => {
      const src = thumb.getAttribute("data-src");

      if (!src) {
        return;
      }

      main.src = src;
      thumbs.forEach((item) => {
        const isActive = item === thumb;
        item.classList.toggle("product__thumb--active", isActive);
        item.setAttribute("aria-pressed", String(isActive));
      });
    });
  });
}

function initTabs(root) {
  const tabsRoot = root.querySelector("[data-product-tabs]");

  if (!tabsRoot) {
    return;
  }

  const tabs = Array.from(tabsRoot.querySelectorAll("[data-product-tab]"));
  const panels = Array.from(tabsRoot.querySelectorAll("[data-product-panel]"));

  if (tabs.length === 0 || panels.length === 0) {
    return;
  }

  const activate = (key) => {
    tabs.forEach((tab) => {
      const isActive = tab.getAttribute("data-product-tab") === key;
      tab.setAttribute("aria-selected", String(isActive));
      tab.tabIndex = isActive ? 0 : -1;
      tab.classList.toggle("product-tabs__tab--active", isActive);
    });

    panels.forEach((panel) => {
      const isActive = panel.getAttribute("data-product-panel") === key;
      panel.hidden = !isActive;
    });
  };

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => {
      activate(tab.getAttribute("data-product-tab"));
    });

    tab.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowRight" && event.key !== "ArrowLeft" && event.key !== "Home" && event.key !== "End") {
        return;
      }

      event.preventDefault();
      let nextIndex = index;

      if (event.key === "ArrowRight") {
        nextIndex = (index + 1) % tabs.length;
      } else if (event.key === "ArrowLeft") {
        nextIndex = (index - 1 + tabs.length) % tabs.length;
      } else if (event.key === "Home") {
        nextIndex = 0;
      } else if (event.key === "End") {
        nextIndex = tabs.length - 1;
      }

      const next = tabs[nextIndex];
      next.focus();
      activate(next.getAttribute("data-product-tab"));
    });
  });

  const initial = tabs.find((tab) => tab.getAttribute("aria-selected") === "true") || tabs[0];
  activate(initial.getAttribute("data-product-tab"));
}
