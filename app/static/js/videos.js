(function initVideosBlock() {
  function init() {
    const root = document.querySelector("[data-videos]");

    if (!root || root.dataset.videosReady === "true") {
      return;
    }

    root.dataset.videosReady = "true";

    const featuredMedia = root.querySelector("[data-videos-featured-media]");
    const featuredThumb = root.querySelector("[data-videos-featured-thumb]");
    const featuredTitle = root.querySelector("[data-videos-featured-title]");
    const featuredText = root.querySelector("[data-videos-featured-text]");
    const overlay = root.querySelector("[data-videos-overlay]");
    const cards = Array.from(root.querySelectorAll("[data-videos-card]"));
    const modal = root.querySelector("[data-videos-modal]");
    const modalFrame = root.querySelector("[data-videos-modal-frame]");
    const modalClose = root.querySelector("[data-videos-modal-close]");

    let activeEmbed = featuredMedia?.dataset.embed || "";

    function setActiveCard(card) {
      cards.forEach((item) => {
        item.classList.toggle("is-active", item === card);
        item.setAttribute("aria-pressed", item === card ? "true" : "false");
      });
    }

    function renderOverlay(lines) {
      if (!overlay) {
        return;
      }

      overlay.replaceChildren();

      lines
        .map((line) => line.trim())
        .filter(Boolean)
        .forEach((line) => {
          const span = document.createElement("span");
          span.className = "videos__overlay-line";
          span.textContent = line;
          overlay.appendChild(span);
        });
    }

    function applyVideo(card) {
      const {
        title = "",
        description = "",
        thumb = "",
        embed = "",
        overlay: overlayRaw = "",
      } = card.dataset;

      if (featuredThumb && thumb) {
        featuredThumb.src = thumb;
        featuredThumb.alt = title;
      }

      if (featuredTitle) {
        featuredTitle.textContent = title;
      }

      if (featuredText) {
        featuredText.textContent = description;
      }

      renderOverlay(overlayRaw.split("|"));
      activeEmbed = embed;

      if (featuredMedia) {
        featuredMedia.dataset.embed = embed;
      }

      setActiveCard(card);
    }

    function openModal() {
      if (!modal || !modalFrame || !activeEmbed) {
        return;
      }

      modalFrame.replaceChildren();

      const iframe = document.createElement("iframe");
      iframe.src = `${activeEmbed}?autoplay=1`;
      iframe.title = featuredTitle?.textContent || "Видео";
      iframe.allow =
        "clipboard-write; autoplay; encrypted-media; fullscreen; picture-in-picture";
      iframe.allowFullscreen = true;
      iframe.referrerPolicy = "strict-origin-when-cross-origin";
      modalFrame.appendChild(iframe);

      modal.hidden = false;
      document.body.style.overflow = "hidden";
      modalClose?.focus();
    }

    function closeModal() {
      if (!modal || !modalFrame) {
        return;
      }

      modal.hidden = true;
      modalFrame.replaceChildren();
      document.body.style.overflow = "";
    }

    cards.forEach((card) => {
      card.addEventListener("click", () => {
        applyVideo(card);
      });
    });

    featuredMedia?.addEventListener("click", () => {
      openModal();
    });

    modalClose?.addEventListener("click", () => {
      closeModal();
    });

    modal?.addEventListener("click", (event) => {
      if (event.target === modal) {
        closeModal();
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && modal && !modal.hidden) {
        closeModal();
      }
    });

    const initial = cards.find((card) => card.classList.contains("is-active"));

    if (initial) {
      applyVideo(initial);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
