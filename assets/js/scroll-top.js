(() => {
  const THRESHOLD_PX = 240;
  const FOOTER_GAP_PX = 12;
  const MAX_FOOTER_LIFT_RATIO = 0.45;

  const button = document.querySelector("[data-floating-scroll-top]");
  const root = document.querySelector("[data-floating-actions]");
  const footer = document.querySelector("[data-site-footer]");

  if (!button) {
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

  const setVisible = (shouldShow) => {
    button.classList.toggle("is-visible", shouldShow);
    button.tabIndex = shouldShow ? 0 : -1;
    button.setAttribute("aria-hidden", String(!shouldShow));

    if (!shouldShow && document.activeElement === button) {
      button.blur();
    }
  };

  const updateFooterOffset = () => {
    if (!root || !footer) {
      root?.style.removeProperty("--floating-bottom");
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

  const update = () => {
    frameId = 0;
    setVisible(getScrollY() > THRESHOLD_PX);
    updateFooterOffset();
  };

  const requestUpdate = () => {
    if (frameId) {
      return;
    }

    frameId = window.requestAnimationFrame(update);
  };

  button.tabIndex = -1;
  button.setAttribute("aria-hidden", "true");
  update();

  window.addEventListener("scroll", requestUpdate, { passive: true });
  document.addEventListener("scroll", requestUpdate, {
    passive: true,
    capture: true,
  });
  window.addEventListener("resize", requestUpdate, { passive: true });
  window.addEventListener("load", requestUpdate, { passive: true });

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

        setVisible(!entry.isIntersecting);
        updateFooterOffset();
      },
      { threshold: 0 },
    );

    observer.observe(sentinel);
  }

  button.addEventListener("click", (event) => {
    event.preventDefault();

    const behavior = prefersReducedMotion() ? "auto" : "smooth";

    window.scrollTo({ top: 0, behavior });
    document.documentElement.scrollTo?.({ top: 0, behavior });
    document.body.scrollTo?.({ top: 0, behavior });
  });
})();
