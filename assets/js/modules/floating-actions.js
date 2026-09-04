const FOOTER_GAP_PX = 12;
const MAX_FOOTER_LIFT_RATIO = 0.45;

export function initFloatingActions() {
  const root = document.querySelector("[data-floating-actions]");

  if (!root) {
    return;
  }

  const chatRoot = root.querySelector("[data-floating-chat]");
  const chatToggle = root.querySelector("[data-floating-chat-toggle]");
  const chatPanel = root.querySelector("[data-floating-chat-panel]");
  const footer = document.querySelector("[data-site-footer]");

  if (!chatRoot || !chatToggle || !chatPanel) {
    return;
  }

  let isChatOpen = false;

  const setChatOpen = (nextOpen, { restoreFocus = false } = {}) => {
    if (nextOpen === isChatOpen) {
      if (restoreFocus) {
        chatToggle.focus();
      }

      return;
    }

    isChatOpen = nextOpen;
    root.classList.toggle("is-chat-open", isChatOpen);
    chatToggle.setAttribute("aria-expanded", String(isChatOpen));
    chatToggle.setAttribute(
      "aria-label",
      isChatOpen ? "Закрыть чат" : "Открыть чат",
    );
    chatPanel.hidden = !isChatOpen;

    if (restoreFocus) {
      chatToggle.focus();
    }
  };

  const updateFooterOffset = () => {
    if (!footer) {
      root.style.removeProperty("--floating-bottom");
      return;
    }

    const footerTop = footer.getBoundingClientRect().top;
    const overlap = Math.max(0, window.innerHeight - footerTop);
    const maxLift = window.innerHeight * MAX_FOOTER_LIFT_RATIO;
    const bottom = Math.min(
      overlap > 0 ? overlap + FOOTER_GAP_PX : 0,
      maxLift,
    );

    if (bottom > 0) {
      root.style.setProperty("--floating-bottom", `${bottom}px`);
      return;
    }

    root.style.removeProperty("--floating-bottom");
  };

  let frameId = 0;

  const requestUpdate = () => {
    if (frameId) {
      return;
    }

    frameId = window.requestAnimationFrame(() => {
      frameId = 0;
      updateFooterOffset();
    });
  };

  chatToggle.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    setChatOpen(!isChatOpen);
  });

  chatPanel.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      setChatOpen(false);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && isChatOpen) {
      setChatOpen(false, { restoreFocus: true });
    }
  });

  document.addEventListener("pointerdown", (event) => {
    if (!isChatOpen || chatRoot.contains(event.target)) {
      return;
    }

    setChatOpen(false);
  });

  setChatOpen(false);
  updateFooterOffset();

  window.addEventListener("scroll", requestUpdate, { passive: true });
  document.addEventListener("scroll", requestUpdate, {
    passive: true,
    capture: true,
  });
  window.addEventListener("resize", requestUpdate, { passive: true });
}
