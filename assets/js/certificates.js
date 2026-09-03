(function initCertificatesLightbox() {
  function init() {
    const root = document.querySelector("[data-certificates]");

    if (!root || root.dataset.certificatesReady === "true") {
      return;
    }

    root.dataset.certificatesReady = "true";

    const lightbox = root.querySelector("[data-certificates-lightbox]");
    const lightboxImage = root.querySelector("[data-certificates-lightbox-image]");
    const lightboxClose = root.querySelector("[data-certificates-lightbox-close]");

    if (!lightbox || !lightboxImage) {
      return;
    }

    function closeLightbox() {
      lightbox.hidden = true;
      lightboxImage.removeAttribute("src");
      lightboxImage.alt = "";
      document.body.style.overflow = "";
    }

    function openLightbox(src, alt) {
      lightboxImage.src = src;
      lightboxImage.alt = alt || "Аттестат аккредитации";
      lightbox.hidden = false;
      document.body.style.overflow = "hidden";
    }

    root.addEventListener("click", function (event) {
      const trigger = event.target.closest("[data-certificates-open]");

      if (!trigger || !root.contains(trigger)) {
        return;
      }

      event.preventDefault();
      openLightbox(
        trigger.getAttribute("data-certificates-open") || "",
        trigger.getAttribute("data-certificates-alt") || "Аттестат аккредитации",
      );
    });

    if (lightboxClose) {
      lightboxClose.addEventListener("click", closeLightbox);
    }

    lightbox.addEventListener("click", function (event) {
      if (event.target === lightbox) {
        closeLightbox();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !lightbox.hidden) {
        closeLightbox();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
