const STORAGE_KEY = "laminatperm_cookie_notice_accepted_v2";

export function initCookieBanner() {
  const banner = document.querySelector("[data-cookie-banner]");
  const button = banner?.querySelector("[data-cookie-accept]");
  const root = document.documentElement;

  if (!banner || !button) {
    return;
  }

  const clearFloatingOffset = () => {
    root.classList.remove("has-cookie-banner");
    root.style.removeProperty("--cookie-banner-offset");
  };

  const updateFloatingOffset = () => {
    const bannerHeight = banner.getBoundingClientRect().height;

    root.classList.add("has-cookie-banner");
    root.style.setProperty(
      "--cookie-banner-offset",
      `${Math.ceil(bannerHeight + 24)}px`,
    );
  };

  try {
    if (window.localStorage.getItem(STORAGE_KEY) === "1") {
      clearFloatingOffset();
      return;
    }
  } catch (error) {
    console.warn("[laminatperm] cookie storage unavailable:", error);
  }

  banner.hidden = false;
  updateFloatingOffset();

  window.addEventListener("resize", updateFloatingOffset, { passive: true });
  window.visualViewport?.addEventListener("resize", updateFloatingOffset, {
    passive: true,
  });

  button.addEventListener("click", () => {
    banner.hidden = true;
    clearFloatingOffset();

    try {
      window.localStorage.setItem(STORAGE_KEY, "1");
    } catch (error) {
      console.warn("[laminatperm] cookie storage unavailable:", error);
    }
  });
}
