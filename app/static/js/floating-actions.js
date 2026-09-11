(() => {
  const SCROLL_TOP_THRESHOLD_PX = 240;
  const FOOTER_GAP_PX = 20;

  const root = document.querySelector("[data-floating-actions]");
  const chatRoot = root?.querySelector("[data-floating-chat]");
  const chatToggle = root?.querySelector("[data-floating-chat-toggle]");
  const chatPanel = root?.querySelector("[data-floating-chat-panel]");
  const scrollTopButton = root?.querySelector("[data-floating-scroll-top]");
  const footer = document.querySelector("[data-site-footer]");

  if (!root) {
    return;
  }

  const prefersReducedMotion = () =>
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const getScrollY = () =>
    window.scrollY ||
    window.pageYOffset ||
    document.scrollingElement?.scrollTop ||
    document.documentElement.scrollTop ||
    document.body.scrollTop ||
    0;

  let isChatOpen = false;
  let frameId = 0;

  const setChatOpen = (nextOpen, { restoreFocus = false } = {}) => {
    if (!chatRoot || !chatToggle || !chatPanel) {
      return;
    }

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

  const setScrollTopVisible = (shouldShow) => {
    if (!scrollTopButton) {
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
      root.style.setProperty("--floating-offset", "0px");
      return;
    }

    const footerTop = footer.getBoundingClientRect().top;
    const rootHeight = root.getBoundingClientRect().height || 0;
    const overlap = window.innerHeight - footerTop;

    if (overlap <= 0) {
      root.style.setProperty("--floating-offset", "0px");
      return;
    }

    const maxOffset = Math.max(0, window.innerHeight - rootHeight - 16);
    const offset = Math.min(overlap + FOOTER_GAP_PX, maxOffset);

    root.style.setProperty("--floating-offset", `${Math.round(offset)}px`);
  };

  const update = () => {
    frameId = 0;
    setScrollTopVisible(getScrollY() > SCROLL_TOP_THRESHOLD_PX);
    updateFooterOffset();
  };

  const requestUpdate = () => {
    if (frameId) {
      return;
    }

    frameId = window.requestAnimationFrame(update);
  };

  if (chatToggle && chatPanel && chatRoot) {
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

    document.addEventListener("click", (event) => {
      if (!isChatOpen || chatRoot.contains(event.target)) {
        return;
      }

      setChatOpen(false);
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && isChatOpen) {
        setChatOpen(false, { restoreFocus: true });
      }
    });

    setChatOpen(false);
  }

  if (scrollTopButton) {
    scrollTopButton.tabIndex = -1;
    scrollTopButton.setAttribute("aria-hidden", "true");

    scrollTopButton.addEventListener("click", (event) => {
      event.preventDefault();
      setChatOpen(false);

      const behavior = prefersReducedMotion() ? "auto" : "smooth";

      window.scrollTo({ top: 0, behavior });
      document.documentElement.scrollTo?.({ top: 0, behavior });
      document.body.scrollTo?.({ top: 0, behavior });
    });

    const sentinel = document.createElement("div");
    sentinel.setAttribute("aria-hidden", "true");
    sentinel.style.cssText =
      "position:absolute;top:0;left:0;width:1px;height:240px;pointer-events:none;opacity:0;";
    document.body.prepend(sentinel);

    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (!entry) {
            return;
          }

          setScrollTopVisible(!entry.isIntersecting);
          updateFooterOffset();
        },
        { threshold: 0 },
      );

      observer.observe(sentinel);
    }
  }

  update();

  window.addEventListener("scroll", requestUpdate, { passive: true });
  document.addEventListener("scroll", requestUpdate, {
    passive: true,
    capture: true,
  });
  window.addEventListener("resize", requestUpdate, { passive: true });
  window.addEventListener("load", requestUpdate, { passive: true });
})();
