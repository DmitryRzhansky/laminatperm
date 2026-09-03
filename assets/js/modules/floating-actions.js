import { getLenis } from "./scroll.js";

const SCROLL_TOP_THRESHOLD = 320;
const FOOTER_GAP_PX = 12;

function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function initFloatingActions() {
  const root = document.querySelector("[data-floating-actions]");

  if (!root) {
    return;
  }

  const chatRoot = root.querySelector("[data-floating-chat]");
  const chatToggle = root.querySelector("[data-floating-chat-toggle]");
  const chatPanel = root.querySelector("[data-floating-chat-panel]");
  const scrollTopButton = root.querySelector("[data-floating-scroll-top]");
  const footer = document.querySelector("[data-site-footer]");

  if (!chatRoot || !chatToggle || !chatPanel || !scrollTopButton) {
    return;
  }

  const setChatOpen = (isOpen, { restoreFocus = false } = {}) => {
    const wasOpen = chatToggle.getAttribute("aria-expanded") === "true";

    if (isOpen === wasOpen) {
      if (restoreFocus) {
        chatToggle.focus();
      }

      return;
    }

    root.classList.toggle("is-chat-open", isOpen);
    chatToggle.setAttribute("aria-expanded", String(isOpen));
    chatToggle.setAttribute(
      "aria-label",
      isOpen ? "Закрыть чат" : "Открыть чат",
    );
    chatPanel.hidden = !isOpen;

    if (restoreFocus) {
      chatToggle.focus();
    }
  };

  const updateScrollTopVisibility = () => {
    const scrollY = getLenis()?.scroll ?? window.scrollY;
    const shouldShow = scrollY > SCROLL_TOP_THRESHOLD;
    const isVisible = scrollTopButton.classList.contains("is-visible");

    if (shouldShow === isVisible) {
      return;
    }

    scrollTopButton.classList.toggle("is-visible", shouldShow);
    scrollTopButton.tabIndex = shouldShow ? 0 : -1;
    scrollTopButton.setAttribute("aria-hidden", String(!shouldShow));

    if (!shouldShow && document.activeElement === scrollTopButton) {
      scrollTopButton.blur();
    }
  };

  const updateFooterOffset = () => {
    if (!footer) {
      root.style.removeProperty("--floating-bottom");
      return;
    }

    const footerTop = footer.getBoundingClientRect().top;
    const overlap = Math.max(0, window.innerHeight - footerTop);
    const bottom = overlap > 0 ? overlap + FOOTER_GAP_PX : 0;

    if (bottom > 0) {
      root.style.setProperty("--floating-bottom", `${bottom}px`);
      return;
    }

    root.style.removeProperty("--floating-bottom");
  };

  let frameId = 0;

  const update = () => {
    frameId = 0;
    updateScrollTopVisibility();
    updateFooterOffset();
  };

  const requestUpdate = () => {
    if (frameId) {
      return;
    }

    frameId = window.requestAnimationFrame(update);
  };

  const scrollToTop = () => {
    setChatOpen(false);

    const lenis = getLenis();

    if (lenis) {
      lenis.scrollTo(0);
      return;
    }

    window.scrollTo({
      top: 0,
      behavior: prefersReducedMotion() ? "auto" : "smooth",
    });
  };

  chatToggle.addEventListener("click", () => {
    setChatOpen(chatToggle.getAttribute("aria-expanded") !== "true");
  });

  chatPanel.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      setChatOpen(false);
    }
  });

  scrollTopButton.addEventListener("click", scrollToTop);

  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape"
      && chatToggle.getAttribute("aria-expanded") === "true"
    ) {
      setChatOpen(false, { restoreFocus: true });
    }
  });

  document.addEventListener("click", (event) => {
    if (
      chatToggle.getAttribute("aria-expanded") === "true"
      && !chatRoot.contains(event.target)
    ) {
      setChatOpen(false);
    }
  });

  scrollTopButton.tabIndex = -1;
  scrollTopButton.setAttribute("aria-hidden", "true");
  update();

  window.addEventListener("scroll", requestUpdate, { passive: true });
  window.addEventListener("resize", requestUpdate, { passive: true });

  const lenis = getLenis();

  if (lenis) {
    lenis.on("scroll", requestUpdate);
  }
}
