export function initShopFilters() {
  const root = document.querySelector("[data-shop-filters]");

  if (!root) {
    return;
  }

  const dropdowns = Array.from(root.querySelectorAll("[data-shop-filter-dropdown]"));

  function setOpen(dropdown, open) {
    const toggle = dropdown.querySelector("[data-shop-filter-toggle]");
    const panel = dropdown.querySelector("[data-shop-filter-panel]");

    if (!toggle || !panel) {
      return;
    }

    dropdown.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    panel.hidden = !open;
  }

  for (const dropdown of dropdowns) {
    const toggle = dropdown.querySelector("[data-shop-filter-toggle]");

    if (!toggle) {
      continue;
    }

    toggle.addEventListener("click", () => {
      const willOpen = !dropdown.classList.contains("is-open");

      for (const other of dropdowns) {
        setOpen(other, other === dropdown ? willOpen : false);
      }
    });
  }

  const autoInputs = root.querySelectorAll("[data-shop-filter-auto]");

  for (const input of autoInputs) {
    input.addEventListener("change", () => {
      if (typeof root.requestSubmit === "function") {
        root.requestSubmit();
        return;
      }

      root.submit();
    });
  }
}
