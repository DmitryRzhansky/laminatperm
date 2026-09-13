const STORAGE_KEY = "laminatperm_cookie_notice_accepted";

export function initCookieBanner() {
  const banner = document.querySelector("[data-cookie-banner]");
  const button = banner?.querySelector("[data-cookie-accept]");

  if (!banner || !button) {
    return;
  }

  try {
    if (window.localStorage.getItem(STORAGE_KEY) === "1") {
      return;
    }
  } catch (error) {
    console.warn("[laminatperm] cookie storage unavailable:", error);
  }

  banner.hidden = false;

  button.addEventListener("click", () => {
    banner.hidden = true;

    try {
      window.localStorage.setItem(STORAGE_KEY, "1");
    } catch (error) {
      console.warn("[laminatperm] cookie storage unavailable:", error);
    }
  });
}
