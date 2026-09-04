import { initFadeMotion } from "./modules/motion.js";
import { initMenu } from "./modules/menu.js";
import { initPartners } from "./modules/partners.js";
import { initSmoothScroll } from "./modules/scroll.js";
import { initFloatingActions } from "./modules/floating-actions.js";

function initHeroVideo() {
  const video = document.querySelector("[data-hero-video]");
  const poster = document.querySelector("[data-hero-poster]");
  const playButton = document.querySelector("[data-hero-play]");

  if (!video || !playButton) {
    return;
  }

  const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const playIcon = playButton.querySelector(".hero__play-icon path");
  const playPath =
    "M232.4,114.49,88.32,26.35a16,16,0,0,0-16.2-.3A15.86,15.86,0,0,0,64,39.87V216.13A15.94,15.94,0,0,0,80,232a16.07,16.07,0,0,0,8.36-2.35L232.4,141.51a15.81,15.81,0,0,0,0-27ZM80,215.94V40l143.83,88Z";
  const pausePath =
    "M200,32H160a16,16,0,0,0-16,16V208a16,16,0,0,0,16,16h40a16,16,0,0,0,16-16V48A16,16,0,0,0,200,32Zm0,176H160V48h40ZM96,32H56A16,16,0,0,0,40,48V208a16,16,0,0,0,16,16H96a16,16,0,0,0,16-16V48A16,16,0,0,0,96,32Zm0,176H56V48H96Z";

  const showPausedState = () => {
    video.classList.add("hero__video--paused");
    poster?.classList.remove("hero__poster--hidden");
    playButton.classList.remove("hero__play--playing");
    playButton.setAttribute("aria-label", "Смотреть видео");
    if (playIcon) {
      playIcon.setAttribute("d", playPath);
    }
  };

  const showPlayingState = () => {
    video.classList.remove("hero__video--paused");
    poster?.classList.add("hero__poster--hidden");
    playButton.classList.add("hero__play--playing");
    playButton.setAttribute("aria-label", "Остановить видео");
    if (playIcon) {
      playIcon.setAttribute("d", pausePath);
    }
  };

  const pauseVideo = () => {
    video.pause();
    showPausedState();
  };

  const playVideo = () => {
    if (motionQuery.matches) {
      pauseVideo();
      return;
    }

    video.muted = true;
    video.playsInline = true;

    const playPromise = video.play();

    if (playPromise && typeof playPromise.then === "function") {
      playPromise.then(showPlayingState).catch(() => {
        showPausedState();
      });
      return;
    }

    showPlayingState();
  };

  if (motionQuery.matches) {
    pauseVideo();
    playButton.hidden = true;
    return;
  }

  showPausedState();

  playButton.addEventListener("click", () => {
    if (video.paused) {
      playVideo();
      return;
    }

    pauseVideo();
  });

  video.addEventListener("pause", () => {
    if (!video.ended) {
      showPausedState();
    }
  });

  video.addEventListener("playing", showPlayingState);
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
