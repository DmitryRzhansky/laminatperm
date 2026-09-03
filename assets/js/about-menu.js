(function initAboutMenu() {
  var DESKTOP_MQ = "(min-width: 64rem)";
  var CLOSE_DELAY_MS = 180;

  function bindDesktop(item) {
    var trigger = item.querySelector("[data-about-menu-trigger]");
    var panel = item.querySelector("[data-about-menu-panel]");
    if (!trigger || !panel) return;

    var closeTimer = null;
    var desktopMq = window.matchMedia(DESKTOP_MQ);

    function isDesktop() {
      return desktopMq.matches;
    }

    function isOpen() {
      return item.classList.contains("is-open");
    }

    function openMenu() {
      if (!isDesktop()) return;
      window.clearTimeout(closeTimer);
      item.classList.add("is-open");
      trigger.classList.add("hero-header__nav-link--active");
      trigger.setAttribute("aria-expanded", "true");
      panel.hidden = false;
    }

    function closeMenu() {
      window.clearTimeout(closeTimer);
      item.classList.remove("is-open");
      trigger.classList.remove("hero-header__nav-link--active");
      trigger.setAttribute("aria-expanded", "false");
      panel.hidden = true;
    }

    function scheduleClose() {
      window.clearTimeout(closeTimer);
      closeTimer = window.setTimeout(closeMenu, CLOSE_DELAY_MS);
    }

    function onEnter() {
      if (isDesktop()) openMenu();
    }

    function onLeave(event) {
      if (!isDesktop()) return;
      var next = event.relatedTarget;
      if (next && item.contains(next)) return;
      scheduleClose();
    }

    trigger.addEventListener("mouseenter", onEnter);
    trigger.addEventListener("mouseleave", onLeave);
    panel.addEventListener("mouseenter", onEnter);
    panel.addEventListener("mouseleave", onLeave);

    trigger.addEventListener("click", function (event) {
      if (!isDesktop()) return;
      event.preventDefault();
      event.stopPropagation();
      if (isOpen()) closeMenu();
      else openMenu();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && isOpen()) {
        closeMenu();
        trigger.focus();
      }
    });

    document.addEventListener("mousedown", function (event) {
      if (!isOpen() || !isDesktop()) return;
      if (item.contains(event.target)) return;
      closeMenu();
    });

    if (desktopMq.addEventListener) {
      desktopMq.addEventListener("change", function (event) {
        if (!event.matches && isOpen()) closeMenu();
      });
    }
  }

  function bindMobile(root) {
    var trigger = root.querySelector("[data-about-mobile-trigger]");
    var panel = root.querySelector("[data-about-mobile-panel]");
    if (!trigger || !panel) return;

    trigger.addEventListener("click", function () {
      var willOpen = panel.hidden;
      root.classList.toggle("is-open", willOpen);
      trigger.setAttribute("aria-expanded", String(willOpen));
      panel.hidden = !willOpen;
    });
  }

  function init() {
    var desktopItem = document.querySelector("[data-about-menu]");
    var mobileRoot = document.querySelector("[data-about-menu-mobile]");

    if (desktopItem && desktopItem.getAttribute("data-ready") !== "true") {
      desktopItem.setAttribute("data-ready", "true");
      bindDesktop(desktopItem);
    }

    if (mobileRoot && mobileRoot.getAttribute("data-ready") !== "true") {
      mobileRoot.setAttribute("data-ready", "true");
      bindMobile(mobileRoot);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
