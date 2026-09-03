import { initFadeMotion } from "./modules/motion.js";
import { initMenu } from "./modules/menu.js";
import { initPartners } from "./modules/partners.js";
import { initSmoothScroll } from "./modules/scroll.js";
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

  const prepareVideo = () => {
    video.muted = true;
    video.defaultMuted = true;
    video.playsInline = true;
    video.setAttribute("muted", "");
    video.setAttribute("playsinline", "");
    video.setAttribute("webkit-playsinline", "");
  };

  const tryPlay = () => {
    if (motionQuery.matches) {
      video.pause();
      showPoster();
      return;
    }

    prepareVideo();

    const playPromise = video.play();

    if (playPromise && typeof playPromise.then === "function") {
      playPromise.then(hidePoster).catch(() => {
        poster?.classList.remove("hero__poster--hidden");
      });
    }
  };

  if (motionQuery.matches) {
    video.pause();
    showPoster();
    return;
  }

  prepareVideo();
  video.addEventListener("playing", hidePoster);
  video.addEventListener("canplay", tryPlay, { once: true });
  video.addEventListener("ended", () => {
    video.currentTime = 0;
    tryPlay();
  });
  tryPlay();

  const unlock = () => {
    if (video.paused) {
      tryPlay();
    }
  };

  ["pointerdown", "touchstart", "keydown"].forEach((eventName) => {
    document.addEventListener(eventName, unlock, { passive: true });
  });

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible" && video.paused) {
      tryPlay();
    }
  });

  window.addEventListener("pageshow", () => {
    if (video.paused) {
      tryPlay();
    }
  });
}

function safeInit(label, fn) {
  try {
    fn();
  } catch (error) {
    console.error(`[sanexpert] ${label} failed:`, error);
  }
}

if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  document.documentElement.classList.add("has-motion");
}

safeInit("smooth-scroll", initSmoothScroll);
safeInit("mobile-menu", initMenu);
safeInit("partners", initPartners);
safeInit("hero-video", initHeroVideo);
safeInit("fade-motion", initFadeMotion);
safeInit("floating-actions", initFloatingActions);
