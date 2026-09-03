const FADE_TARGETS = [
  ".hero__content",
  ".about__inner",
  ".advantages__inner",
  ".services__inner",
  ".catalog__inner",
  ".partners__inner",
  ".reviews__inner",
  ".videos__inner",
  ".faq__inner",
  ".contact-section__inner",
  ".site-footer",
];

export function initFadeMotion() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  const elements = FADE_TARGETS.flatMap((selector) =>
    Array.from(document.querySelectorAll(selector))
  );

  if (elements.length === 0) {
    return;
  }

  elements.forEach((element) => {
    element.setAttribute("data-fade", "");
  });

  const hero = document.querySelector(".hero__content[data-fade]");

  if (hero) {
    requestAnimationFrame(() => {
      hero.classList.add("is-visible");
    });
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    {
      root: null,
      rootMargin: "0px 0px -24px 0px",
      threshold: 0,
    }
  );

  elements.forEach((element) => {
    if (element === hero) {
      return;
    }

    observer.observe(element);
  });
}
