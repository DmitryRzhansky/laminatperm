import { initFadeMotion } from "./modules/motion.js";
import { initMenu } from "./modules/menu.js";
import { initPartners } from "./modules/partners.js";
import { initScroll } from "./modules/scroll.js";
import { initFloatingActions } from "./modules/floating-actions.js";

function initHeroVideo() {
  const video = document.querySelector("[data-hero-video]");
  const poster = document.querySelector("[data-hero-poster]");

  if (!video) {
    return;
  }

  const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");

  const showPoster = () => {
    video.classList.add("hero__video--paused");
    poster?.classList.remove("hero__poster--hidden");
  };

  const hidePoster = () => {
    video.classList.remove("hero__video--paused");
    poster?.classList.add("hero__poster--hidden");
  };

  const playMuted = () => {
    if (motionQuery.matches) {
      video.pause();
      showPoster();
      return;
    }

    video.muted = true;
    video.defaultMuted = true;
    video.playsInline = true;

    const playPromise = video.play();

    if (playPromise && typeof playPromise.then === "function") {
      playPromise.then(hidePoster).catch(showPoster);
      return;
    }

    hidePoster();
  };

  if (motionQuery.matches) {
    video.pause();
    showPoster();
    return;
  }

  video.addEventListener("playing", hidePoster);
  playMuted();
}

function safeInit(label, fn) {
  try {
    fn();
  } catch (error) {
    console.error(`[laminatperm] ${label} failed:`, error);
  }
}

if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  document.documentElement.classList.add("has-motion");
}

safeInit("scroll", initScroll);
safeInit("mobile-menu", initMenu);
safeInit("partners", initPartners);
safeInit("hero-video", initHeroVideo);
safeInit("fade-motion", initFadeMotion);
safeInit("floating-actions", initFloatingActions);
