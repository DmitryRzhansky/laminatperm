(function initMobileMenu() {
  var menu = document.querySelector("[data-mobile-menu]");
  var toggle = document.querySelector("[data-menu-toggle]");

  if (!menu || !toggle) {
    return;
  }

  var lastFocused = null;
  var closeArmed = true;
  var closeArmTimer = null;
  var desktopMq = window.matchMedia("(min-width: 64rem)");

  function isOpen() {
    return document.body.classList.contains("is-menu-open");
  }

  function openMenu() {
    lastFocused = document.activeElement;
    closeArmed = false;
    window.clearTimeout(closeArmTimer);

    menu.hidden = false;
    menu.removeAttribute("hidden");
    menu.classList.add("is-open");
    menu.setAttribute("aria-hidden", "false");

    document.documentElement.classList.add("is-menu-open", "is-scroll-locked");
    document.body.classList.add("is-menu-open", "is-scroll-locked");

    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Закрыть меню");

    closeArmTimer = window.setTimeout(function () {
      closeArmed = true;
    }, 400);
  }

  function closeMenu() {
    window.clearTimeout(closeArmTimer);
    closeArmed = true;

    menu.classList.remove("is-open");
    menu.hidden = true;
    menu.setAttribute("hidden", "");
    menu.setAttribute("aria-hidden", "true");

    document.documentElement.classList.remove("is-menu-open", "is-scroll-locked");
    document.body.classList.remove("is-menu-open", "is-scroll-locked");

    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Открыть меню");

    if (lastFocused && typeof lastFocused.focus === "function") {
      lastFocused.focus({ preventScroll: true });
    } else {
      toggle.focus({ preventScroll: true });
    }
  }

  function toggleMenu(event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    if (isOpen()) {
      closeMenu();
    } else {
      openMenu();
    }
  }

  document.addEventListener(
    "click",
    function (event) {
      var toggleButton = event.target.closest("[data-menu-toggle]");

      if (toggleButton) {
        toggleMenu(event);
        return;
      }

      if (!isOpen() || !closeArmed) {
        return;
      }

      var closeTarget = event.target.closest("[data-menu-close]");
      if (closeTarget) {
        // Anchors must keep default navigation; only block non-link close controls.
        if (!(closeTarget instanceof HTMLAnchorElement)) {
          event.preventDefault();
        }
        closeMenu();
      }
    },
    true
  );

  document.addEventListener("keydown", function (event) {
    if (!isOpen()) {
      return;
    }

    if (event.key === "Escape") {
      event.preventDefault();
      closeMenu();
    }
  });

  function onDesktopChange(event) {
    if (event.matches && isOpen()) {
      closeMenu();
    }
  }

  if (typeof desktopMq.addEventListener === "function") {
    desktopMq.addEventListener("change", onDesktopChange);
  } else if (typeof desktopMq.addListener === "function") {
    desktopMq.addListener(onDesktopChange);
  }
})();
