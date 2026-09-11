import { pauseScroll, resumeScroll } from "./scroll.js";

export function initMenu() {
  const menu = document.querySelector("[data-mobile-menu]");
  const toggle = document.querySelector("[data-menu-toggle]");

  if (!menu || !toggle) {
    return;
  }

  const focusableSelector =
    'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])';
  let lastFocused = null;

  function getFocusable() {
    return Array.from(menu.querySelectorAll(focusableSelector)).filter((el) => {
      if (el.closest("[hidden]") || el.getAttribute("aria-hidden") === "true") {
        return false;
      }

      const styles = window.getComputedStyle(el);
      return styles.display !== "none" && styles.visibility !== "hidden";
    });
  }

  function openMenu() {
    lastFocused = document.activeElement;
    document.documentElement.classList.add("is-menu-open");
    document.body.classList.add("is-menu-open");
    pauseScroll();
    menu.hidden = false;
    menu.setAttribute("aria-hidden", "false");
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Закрыть меню");

    const closeButton = menu.querySelector(".mobile-menu__close");
    if (closeButton) {
      closeButton.focus({ preventScroll: true });
    }
  }

  function closeMenu() {
    menu.hidden = true;
    menu.setAttribute("aria-hidden", "true");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Открыть меню");
    document.documentElement.classList.remove("is-menu-open");
    document.body.classList.remove("is-menu-open");
    resumeScroll();

    const focusOptions = { preventScroll: true };

    if (lastFocused && typeof lastFocused.focus === "function") {
      lastFocused.focus(focusOptions);
    } else {
      toggle.focus(focusOptions);
    }
  }

  function isOpen() {
    return !menu.hidden;
  }

  toggle.addEventListener("click", () => {
    if (isOpen()) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  menu.addEventListener("click", (event) => {
    const closeTarget = event.target.closest("[data-menu-close]");
    if (closeTarget) {
      closeMenu();
    }
  });

  menu.addEventListener("keydown", (event) => {
    if (!isOpen()) {
      return;
    }

    if (event.key === "Escape") {
      event.preventDefault();
      closeMenu();
      return;
    }

    if (event.key !== "Tab") {
      return;
    }

    const focusable = getFocusable();
    if (focusable.length === 0) {
      return;
    }

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  window.matchMedia("(min-width: 64rem)").addEventListener("change", (event) => {
    if (event.matches && isOpen()) {
      closeMenu();
    }
  });
}
