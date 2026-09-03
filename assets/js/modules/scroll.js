import Lenis from "../../vendor/lenis/lenis.mjs";

let lenis = null;

function getHeaderOffset() {
  const value = getComputedStyle(document.documentElement).getPropertyValue("--header-offset");
  return Number.parseFloat(value) || 0;
}

function bindHeaderScrollState() {
  const header = document.querySelector("[data-header]");

  if (!header || !lenis) {
    return;
  }

  lenis.on("scroll", ({ scroll }) => {
    header.classList.toggle("hero-header--scrolled", scroll > 24);
  });
}

export function initSmoothScroll() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return null;
  }

  lenis = new Lenis({
    duration: 1.2,
    easing: (t) => 1 - (1 - t) ** 3,
    smoothWheel: true,
    wheelMultiplier: 0.8,
    touchMultiplier: 1,
    anchors: {
      offset: -getHeaderOffset(),
    },
  });

  function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
  }

  requestAnimationFrame(raf);
  bindHeaderScrollState();

  return lenis;
}

export function getLenis() {
  return lenis;
}

export function pauseScroll() {
  lenis?.stop();
}

export function resumeScroll() {
  lenis?.start();
}
