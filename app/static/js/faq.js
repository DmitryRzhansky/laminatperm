(function initFaqAccordion() {
  function initRoot(root) {
    if (!root || root.dataset.faqReady === "true") {
      return;
    }

    root.dataset.faqReady = "true";

    const items = Array.from(root.querySelectorAll("[data-faq-item]"));

    function setOpen(item, isOpen) {
      const trigger = item.querySelector("[data-faq-trigger]");
      const panel = item.querySelector("[data-faq-panel]");

      if (!trigger || !panel) {
        return;
      }

      item.classList.toggle("is-open", isOpen);
      trigger.setAttribute("aria-expanded", String(isOpen));
      panel.setAttribute("aria-hidden", String(!isOpen));
    }

    items.forEach((item) => {
      const trigger = item.querySelector("[data-faq-trigger]");

      if (!trigger) {
        return;
      }

      trigger.addEventListener("click", () => {
        const willOpen = !item.classList.contains("is-open");

        items.forEach((otherItem) => {
          setOpen(otherItem, willOpen && otherItem === item);
        });
      });
    });
  }

  function init() {
    document.querySelectorAll("[data-faq]").forEach(initRoot);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
