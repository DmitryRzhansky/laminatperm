(function initServicesMegaMenu() {
  var DESKTOP_MQ = "(min-width: 64rem)";
  var CLOSE_DELAY_MS = 180;

  var categories = [
    {
      title: "Проектная документация",
      url: "#",
      icon: "assets/icons/services/szz.svg",
      services: [
        { title: "Оценка риска здоровью населения", url: "#" },
        { title: "Экспертиза СЗЗ", url: "#" },
        { title: "Экспертиза НДВ", url: "#" },
        { title: "Экспертиза ПДВ", url: "#" },
        { title: "Экспертиза ПРТО / РЭС", url: "#" },
        { title: "Экспертиза приаэродромной территории", url: "#" },
      ],
    },
    {
      title: "Вода и водные объекты",
      url: "#",
      icon: "assets/icons/services/zso.svg",
      services: [
        { title: "Экспертиза ЗСО", url: "#" },
        { title: "Экспертиза НДС", url: "#" },
        { title: "Экспертиза водопользования", url: "#" },
      ],
    },
    {
      title: "Виды деятельности и лицензирование",
      url: "#",
      icon: "assets/icons/services/medical.svg",
      services: [
        { title: "Медицинская деятельность", url: "#" },
        { title: "Образовательная деятельность", url: "#" },
        { title: "Деятельность с опасными отходами", url: "#" },
        { title: "Источники ионизирующего излучения", url: "#" },
      ],
    },
    {
      title: "Перепланировка помещений",
      url: "#",
      icon: "assets/icons/services/replan.svg",
      services: [
        { title: "Коммерческие помещения", url: "#" },
        { title: "Жилые помещения", url: "#" },
      ],
    },
    {
      title: "Лабораторные результаты и отходы",
      url: "#",
      icon: "assets/icons/services/waste.svg",
      services: [
        { title: "Оценка протоколов лабораторных исследований", url: "#" },
        { title: "Санитарно-эпидемиологическая экспертиза отходов", url: "#" },
      ],
    },
  ];

  function esc(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function desktopHtml() {
    var columns = categories
      .map(function (category) {
        var services = category.services
          .map(function (service) {
            return (
              "<li><a class=\"services-menu__link\" href=\"" +
              esc(service.url) +
              "\">" +
              esc(service.title) +
              "</a></li>"
            );
          })
          .join("");

        return (
          "<li class=\"services-menu__column\">" +
          "<div class=\"services-menu__category\">" +
          "<img class=\"services-menu__icon\" src=\"" +
          esc(category.icon) +
          "\" alt=\"\" width=\"40\" height=\"40\">" +
          "<div class=\"services-menu__category-body\">" +
          "<a class=\"services-menu__category-link\" href=\"" +
          esc(category.url) +
          "\">" +
          esc(category.title) +
          "</a>" +
          "<ul class=\"services-menu__list\" role=\"list\">" +
          services +
          "</ul></div></div></li>"
        );
      })
      .join("");

    return (
      "<div class=\"services-menu__panel\" id=\"services-mega-menu\" data-services-menu-panel hidden>" +
      "<ul class=\"services-menu__grid\" role=\"list\">" +
      columns +
      "</ul></div>"
    );
  }

  function mobileHtml() {
    var items = categories
      .map(function (category, index) {
        var panelId = "mobile-services-category-" + index;
        var services = category.services
          .map(function (service) {
            return (
              "<li><a class=\"mobile-menu__services-link\" href=\"" +
              esc(service.url) +
              "\">" +
              esc(service.title) +
              "</a></li>"
            );
          })
          .join("");

        return (
          "<li class=\"mobile-menu__services-category\" data-services-mobile-category>" +
          "<div class=\"mobile-menu__services-category-row\">" +
          "<a class=\"mobile-menu__services-category-link\" href=\"" +
          esc(category.url) +
          "\">" +
          esc(category.title) +
          "</a>" +
          "<button class=\"mobile-menu__services-category-toggle\" type=\"button\" data-services-mobile-category-toggle aria-expanded=\"false\" aria-controls=\"" +
          panelId +
          "\" aria-label=\"Показать услуги: " +
          esc(category.title) +
          "\">" +
          "<svg aria-hidden=\"true\" width=\"16\" height=\"16\" viewBox=\"0 0 256 256\" fill=\"currentColor\"><path d=\"M213.66,101.66l-80,80a8,8,0,0,1-11.32,0l-80-80A8,8,0,0,1,53.66,90.34L128,164.69l74.34-74.35a8,8,0,0,1,11.32,11.32Z\"/></svg>" +
          "</button></div>" +
          "<ul class=\"mobile-menu__services-list\" id=\"" +
          panelId +
          "\" role=\"list\" data-services-mobile-category-panel hidden>" +
          services +
          "</ul></li>"
        );
      })
      .join("");

    return (
      "<button class=\"mobile-menu__services-trigger\" type=\"button\" data-services-mobile-trigger aria-expanded=\"false\" aria-controls=\"mobile-services-panel\">" +
      "Услуги" +
      "<svg class=\"mobile-menu__services-chevron\" aria-hidden=\"true\" width=\"18\" height=\"18\" viewBox=\"0 0 256 256\" fill=\"currentColor\"><path d=\"M213.66,101.66l-80,80a8,8,0,0,1-11.32,0l-80-80A8,8,0,0,1,53.66,90.34L128,164.69l74.34-74.35a8,8,0,0,1,11.32,11.32Z\"/></svg>" +
      "</button>" +
      "<div class=\"mobile-menu__services-panel\" id=\"mobile-services-panel\" data-services-mobile-panel hidden>" +
      "<ul class=\"mobile-menu__services-categories\" role=\"list\">" +
      items +
      "</ul></div>"
    );
  }

  function bindDesktop(item, panel, anchor) {
    var trigger = item.querySelector("[data-services-menu-trigger]");
    if (!trigger || !panel || !anchor) return;

    var closeTimer = null;
    var desktopMq = window.matchMedia(DESKTOP_MQ);

    function isDesktop() {
      return desktopMq.matches;
    }

    function isOpen() {
      return item.classList.contains("is-open");
    }

    function positionPanel() {
      var rect = anchor.getBoundingClientRect();
      panel.style.top = Math.round(rect.bottom + 6) + "px";
      panel.style.left = Math.round(rect.left) + "px";
      panel.style.width = Math.round(rect.width) + "px";
    }

    function openMenu() {
      if (!isDesktop()) return;
      window.clearTimeout(closeTimer);
      positionPanel();
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
      if (next && (item.contains(next) || panel.contains(next))) return;
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
      if (item.contains(event.target) || panel.contains(event.target)) return;
      closeMenu();
    });

    window.addEventListener(
      "resize",
      function () {
        if (isOpen()) positionPanel();
      },
      { passive: true },
    );

    document.addEventListener(
      "scroll",
      function () {
        if (isOpen()) positionPanel();
      },
      { passive: true, capture: true },
    );

    if (desktopMq.addEventListener) {
      desktopMq.addEventListener("change", function (event) {
        if (!event.matches && isOpen()) closeMenu();
      });
    }
  }

  function bindMobile(root) {
    var trigger = root.querySelector("[data-services-mobile-trigger]");
    var panel = root.querySelector("[data-services-mobile-panel]");
    if (!trigger || !panel) return;

    trigger.addEventListener("click", function () {
      var willOpen = panel.hidden;
      root.classList.toggle("is-open", willOpen);
      trigger.setAttribute("aria-expanded", String(willOpen));
      panel.hidden = !willOpen;
    });

    var cats = root.querySelectorAll("[data-services-mobile-category]");
    for (var i = 0; i < cats.length; i += 1) {
      (function (categoryItem) {
        var toggle = categoryItem.querySelector("[data-services-mobile-category-toggle]");
        var categoryPanel = categoryItem.querySelector(
          "[data-services-mobile-category-panel]",
        );
        if (!toggle || !categoryPanel) return;

        toggle.addEventListener("click", function () {
          var willOpen = categoryPanel.hidden;
          categoryItem.classList.toggle("is-open", willOpen);
          toggle.setAttribute("aria-expanded", String(willOpen));
          categoryPanel.hidden = !willOpen;
        });
      })(cats[i]);
    }
  }

  function init() {
    var desktopItem = document.querySelector("[data-services-menu]");
    var headerBody = document.querySelector(".hero-header__body");
    var mobileRoot = document.querySelector("[data-services-menu-mobile]");

    if (desktopItem && headerBody && desktopItem.getAttribute("data-ready") !== "true") {
      desktopItem.setAttribute("data-ready", "true");
      document.body.insertAdjacentHTML("beforeend", desktopHtml());
      bindDesktop(
        desktopItem,
        document.querySelector("[data-services-menu-panel]"),
        headerBody,
      );
    }

    if (mobileRoot && mobileRoot.getAttribute("data-ready") !== "true") {
      mobileRoot.setAttribute("data-ready", "true");
      mobileRoot.innerHTML = mobileHtml();
      bindMobile(mobileRoot);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
