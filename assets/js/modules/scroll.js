function bindHeaderScrollState() {
  const header = document.querySelector("[data-header]");

  if (!header) {
    return;
  }

  const getScrollY = () =>
    window.scrollY ||
    window.pageYOffset ||
    document.scrollingElement?.scrollTop ||
    document.documentElement.scrollTop ||
    document.body.scrollTop ||
    0;

  const update = () => {
    header.classList.toggle("hero-header--scrolled", getScrollY() > 24);
  };

  update();
  window.addEventListener("scroll", update, { passive: true });
  document.addEventListener("scroll", update, { passive: true, capture: true });
}

export function initScroll() {
  bindHeaderScrollState();
}

export function pauseScroll() {
  document.documentElement.classList.add("is-scroll-locked");
  document.body.classList.add("is-scroll-locked");
}

export function resumeScroll() {
  document.documentElement.classList.remove("is-scroll-locked");
  document.body.classList.remove("is-scroll-locked");
}
