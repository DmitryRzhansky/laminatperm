(function initMegaMenus() {
  var DESKTOP_MQ = "(min-width: 64rem)";
  var CLOSE_DELAY_MS = 180;
  var menus = [
    {
      name: "services", label: "Услуги", desktopRoot: "[data-services-menu]", desktopTrigger: "[data-services-menu-trigger]", desktopPanel: "[data-services-menu-panel]", mobileRoot: "[data-services-menu-mobile]", panelId: "services-mega-menu", mobilePanelId: "mobile-services-panel",
      items: [
        { title: "Укладка покрытий", url: "/uslugi", image: "assets/images/menu/services/installation.webp", links: [
          { title: "Укладка ламината", url: "/uslugi/ukladka-laminata" }, { title: "Укладка SPC", url: "/uslugi/ukladka-spc" }, { title: "Укладка кварцвинила и LVT", url: "/uslugi/ukladka-kvartsvinila-lvt" }, { title: "Укладка линолеума", url: "/uslugi/ukladka-linoleuma" }, { title: "Укладка ковролина", url: "/uslugi/ukladka-kovrolina" }
        ] },
        { title: "Подготовка основания", url: "/uslugi/podgotovka-osnovaniya", image: "assets/images/menu/services/subfloor.webp", links: [
          { title: "Проверка перепадов", url: "/uslugi/podgotovka-osnovaniya" }, { title: "Выравнивание пола", url: "/uslugi/podgotovka-osnovaniya" }, { title: "Полусухая стяжка", url: "/uslugi/podgotovka-osnovaniya" }, { title: "Подготовка под тёплый пол", url: "/uslugi/podgotovka-osnovaniya" }
        ] },
        { title: "Демонтаж и подготовка", url: "/uslugi/demontazh-pokrytiya", image: "assets/images/menu/services/demolition.webp", links: [
          { title: "Демонтаж старого покрытия", url: "/uslugi/demontazh-pokrytiya" }, { title: "Очистка основания", url: "/uslugi/demontazh-pokrytiya" }, { title: "Вынос и утилизация", url: "/uslugi/demontazh-pokrytiya" }, { title: "Замер и расчёт материалов", url: "#consultation" }
        ] },
        { title: "Завершение отделки", url: "/uslugi/montazh-plintusa", image: "assets/images/menu/services/finishing.webp", links: [
          { title: "Монтаж плинтуса", url: "/uslugi/montazh-plintusa" }, { title: "Установка порогов", url: "/uslugi/montazh-plintusa" }, { title: "Оформление примыканий", url: "/uslugi/montazh-plintusa" }, { title: "Подрезка дверных коробок", url: "/uslugi/montazh-plintusa" }
        ] }
      ]
    },
    {
      name: "catalog", label: "Каталог", desktopRoot: "[data-catalog-menu]", desktopTrigger: "[data-catalog-menu-trigger]", desktopPanel: "[data-catalog-menu-panel]", mobileRoot: "[data-catalog-menu-mobile]", panelId: "catalog-mega-menu", mobilePanelId: "mobile-catalog-panel",
      items: [
        { title: "Ламинат", url: "/katalog/laminat", image: "assets/images/menu/catalog/laminate.webp", links: makeLinks(["Tarkett", "Egger", "Kronospan", "Classen"], "/katalog/laminat") },
        { title: "SPC", url: "/katalog/spc", image: "assets/images/menu/catalog/spc.webp", links: makeLinks(["Alpine Floor", "Fargo", "Stone Floor", "Vinilam"], "/katalog/spc") },
        { title: "Кварцвинил / LVT", url: "/katalog/kvartsvinil-lvt", image: "assets/images/menu/catalog/lvt.webp", links: makeLinks(["Замковый", "Клеевой", "Под дерево", "Под камень"], "/katalog/kvartsvinil-lvt") },
        { title: "Линолеум", url: "/katalog/linoleum", image: "assets/images/menu/catalog/linoleum.webp", links: makeLinks(["Tarkett", "Juteks", "Sinteros", "Бытовой и коммерческий"], "/katalog/linoleum") },
        { title: "Ковролин", url: "/katalog/kovrolin", image: "assets/images/menu/catalog/carpet.webp", links: makeLinks(["Для дома", "Для офиса", "Короткий ворс", "Ковровая плитка"], "/katalog/kovrolin") },
        { title: "Плинтусы", url: "/katalog/plintusy", image: "assets/images/menu/catalog/skirting.webp", links: makeLinks(["Дюрополимер", "МДФ", "ПВХ", "Теневой профиль"], "/katalog/plintusy") },
        { title: "Подложки", url: "/katalog/podlozhki", image: "assets/images/menu/catalog/underlay.webp", links: makeLinks(["Под ламинат", "Под SPC", "Акустические", "Для тёплого пола"], "/katalog/podlozhki") },
        { title: "Комплектующие", url: "/katalog/komplektuyushchie", image: "assets/images/menu/catalog/accessories.webp", links: makeLinks(["Пороги и профили", "Клей и герметики", "Крепёж", "Средства для ухода"], "/katalog/komplektuyushchie") }
      ]
    }
  ];

  function makeLinks(titles, url) { return titles.map(function (title) { return { title: title, url: url }; }); }
  function esc(value) { return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }

  function desktopHtml(menu) {
    var columns = menu.items.map(function (category) {
      var links = category.links.map(function (link) { return "<li><a class=\"services-menu__link\" href=\"" + esc(link.url) + "\">" + esc(link.title) + "</a></li>"; }).join("");
      return "<li class=\"services-menu__column\"><div class=\"services-menu__category\"><img class=\"services-menu__image\" src=\"" + esc(category.image) + "\" alt=\"\" width=\"160\" height=\"160\" loading=\"lazy\" decoding=\"async\"><div class=\"services-menu__category-body\"><a class=\"services-menu__category-link\" href=\"" + esc(category.url) + "\">" + esc(category.title) + "</a><ul class=\"services-menu__list\" role=\"list\">" + links + "</ul></div></div></li>";
    }).join("");
    return "<div class=\"services-menu__panel services-menu__panel--" + menu.name + "\" id=\"" + menu.panelId + "\" data-" + menu.name + "-menu-panel hidden><ul class=\"services-menu__grid services-menu__grid--" + menu.name + "\" role=\"list\">" + columns + "</ul></div>";
  }

  function mobileHtml(menu) {
    var items = menu.items.map(function (category, index) {
      var panelId = "mobile-" + menu.name + "-category-" + index;
      var links = category.links.map(function (link) { return "<li><a class=\"mobile-menu__services-link\" href=\"" + esc(link.url) + "\" data-menu-close>" + esc(link.title) + "</a></li>"; }).join("");
      return "<li class=\"mobile-menu__services-category\" data-mega-mobile-category><div class=\"mobile-menu__services-category-row\"><img class=\"mobile-menu__services-image\" src=\"" + esc(category.image) + "\" alt=\"\" width=\"96\" height=\"96\" loading=\"lazy\" decoding=\"async\"><a class=\"mobile-menu__services-category-link\" href=\"" + esc(category.url) + "\" data-menu-close>" + esc(category.title) + "</a><button class=\"mobile-menu__services-category-toggle\" type=\"button\" data-mega-mobile-category-toggle aria-expanded=\"false\" aria-controls=\"" + panelId + "\" aria-label=\"Показать разделы: " + esc(category.title) + "\"><svg aria-hidden=\"true\" width=\"16\" height=\"16\" viewBox=\"0 0 256 256\" fill=\"currentColor\"><path d=\"M213.66,101.66l-80,80a8,8,0,0,1-11.32,0l-80-80A8,8,0,0,1,53.66,90.34L128,164.69l74.34-74.35a8,8,0,0,1,11.32,11.32Z\"/></svg></button></div><ul class=\"mobile-menu__services-list\" id=\"" + panelId + "\" role=\"list\" data-mega-mobile-category-panel hidden>" + links + "</ul></li>";
    }).join("");
    return "<button class=\"mobile-menu__services-trigger\" type=\"button\" data-mega-mobile-trigger aria-expanded=\"false\" aria-controls=\"" + menu.mobilePanelId + "\">" + esc(menu.label) + "<svg class=\"mobile-menu__services-chevron\" aria-hidden=\"true\" width=\"18\" height=\"18\" viewBox=\"0 0 256 256\" fill=\"currentColor\"><path d=\"M213.66,101.66l-80,80a8,8,0,0,1-11.32,0l-80-80A8,8,0,0,1,53.66,90.34L128,164.69l74.34-74.35a8,8,0,0,1,11.32,11.32Z\"/></svg></button><div class=\"mobile-menu__services-panel\" id=\"" + menu.mobilePanelId + "\" data-mega-mobile-panel hidden><ul class=\"mobile-menu__services-categories\" role=\"list\">" + items + "</ul></div>";
  }

  function bindDesktop(menu, item, panel, anchor) {
    var trigger = item.querySelector(menu.desktopTrigger);
    if (!trigger || !panel || !anchor) return;
    var closeTimer = null;
    var desktopMq = window.matchMedia(DESKTOP_MQ);
    function isOpen() { return item.classList.contains("is-open"); }
    function positionPanel() { var rect = anchor.getBoundingClientRect(); panel.style.top = Math.round(rect.bottom + 6) + "px"; panel.style.left = Math.round(rect.left) + "px"; panel.style.width = Math.round(rect.width) + "px"; }
    function closeMenu() { window.clearTimeout(closeTimer); item.classList.remove("is-open"); trigger.classList.remove("hero-header__nav-link--active"); trigger.setAttribute("aria-expanded", "false"); panel.hidden = true; }
    function openMenu() { if (!desktopMq.matches) return; document.dispatchEvent(new CustomEvent("mega-menu:open", { detail: item })); window.clearTimeout(closeTimer); positionPanel(); item.classList.add("is-open"); trigger.classList.add("hero-header__nav-link--active"); trigger.setAttribute("aria-expanded", "true"); panel.hidden = false; }
    function scheduleClose() { window.clearTimeout(closeTimer); closeTimer = window.setTimeout(closeMenu, CLOSE_DELAY_MS); }
    function leave(event) { var next = event.relatedTarget; if (next && (item.contains(next) || panel.contains(next))) return; scheduleClose(); }
    trigger.addEventListener("mouseenter", openMenu); trigger.addEventListener("mouseleave", leave); panel.addEventListener("mouseenter", function () { window.clearTimeout(closeTimer); }); panel.addEventListener("mouseleave", leave);
    trigger.addEventListener("click", function (event) { event.preventDefault(); isOpen() ? closeMenu() : openMenu(); });
    document.addEventListener("mega-menu:open", function (event) { if (event.detail !== item) closeMenu(); });
    document.addEventListener("keydown", function (event) { if (event.key === "Escape" && isOpen()) { closeMenu(); trigger.focus(); } });
    document.addEventListener("mousedown", function (event) { if (isOpen() && !item.contains(event.target) && !panel.contains(event.target)) closeMenu(); });
    window.addEventListener("resize", function () { if (isOpen()) positionPanel(); }, { passive: true });
    document.addEventListener("scroll", function () { if (isOpen()) positionPanel(); }, { passive: true, capture: true });
    if (desktopMq.addEventListener) desktopMq.addEventListener("change", function (event) { if (!event.matches) closeMenu(); });
  }

  function bindMobile(root) {
    var trigger = root.querySelector("[data-mega-mobile-trigger]"); var panel = root.querySelector("[data-mega-mobile-panel]");
    if (!trigger || !panel) return;
    trigger.addEventListener("click", function () { var willOpen = panel.hidden; root.classList.toggle("is-open", willOpen); trigger.setAttribute("aria-expanded", String(willOpen)); panel.hidden = !willOpen; });
    var categories = root.querySelectorAll("[data-mega-mobile-category]");
    for (var i = 0; i < categories.length; i += 1) (function (category) {
      var toggle = category.querySelector("[data-mega-mobile-category-toggle]"); var categoryPanel = category.querySelector("[data-mega-mobile-category-panel]");
      if (!toggle || !categoryPanel) return;
      toggle.addEventListener("click", function () { var willOpen = categoryPanel.hidden; category.classList.toggle("is-open", willOpen); toggle.setAttribute("aria-expanded", String(willOpen)); categoryPanel.hidden = !willOpen; });
    })(categories[i]);
  }

  function init() {
    var anchor = document.querySelector(".hero-header__body");
    menus.forEach(function (menu) {
      var desktopRoot = document.querySelector(menu.desktopRoot); var mobileRoot = document.querySelector(menu.mobileRoot);
      if (desktopRoot && anchor) { document.body.insertAdjacentHTML("beforeend", desktopHtml(menu)); bindDesktop(menu, desktopRoot, document.querySelector(menu.desktopPanel), anchor); }
      if (mobileRoot) { mobileRoot.innerHTML = mobileHtml(menu); bindMobile(mobileRoot); }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
