export function initRelatedProducts() {
  const root = document.querySelector("[data-related-products]");

  if (!root) {
    return;
  }

  const viewport = root.querySelector("[data-related-viewport]");
  const track = root.querySelector("[data-related-track]");
  const prevButton = root.querySelector("[data-related-prev]");
  const nextButton = root.querySelector("[data-related-next]");
  const slides = Array.from(root.querySelectorAll(".related-products__slide"));

  if (!viewport || !track || !prevButton || !nextButton || slides.length === 0) {
    return;
  }

  let index = 0;

  const getPerView = () => {
    const raw = getComputedStyle(track).getPropertyValue("--related-per-view").trim();
    const value = Number.parseFloat(raw);
    return Number.isFinite(value) && value > 0 ? value : 1;
  };

  const getStep = () => {
    const styles = getComputedStyle(track);
    const gap = Number.parseFloat(styles.columnGap || styles.gap) || 0;
    return slides[0].getBoundingClientRect().width + gap;
  };

  const maxIndex = () => Math.max(0, slides.length - getPerView());

  const update = () => {
    const max = maxIndex();
    index = Math.min(Math.max(0, index), max);

    const step = getStep();
    track.style.transform = step
      ? `translate3d(-${index * step}px, 0, 0)`
      : "translate3d(0, 0, 0)";

    const canGoPrev = index > 0;
    const canGoNext = index < max;

    prevButton.hidden = !canGoPrev;
    nextButton.hidden = !canGoNext;
    prevButton.disabled = !canGoPrev;
    nextButton.disabled = !canGoNext;
  };

  prevButton.addEventListener("click", () => {
    index -= 1;
    update();
  });

  nextButton.addEventListener("click", () => {
    index += 1;
    update();
  });

  window.addEventListener("resize", () => {
    update();
  });

  requestAnimationFrame(update);
}
