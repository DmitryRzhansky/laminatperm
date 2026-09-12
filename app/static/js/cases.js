(function initCases() {
  function initSlider(root) {
    if (root.dataset.casesReady === "true") {
      return;
    }

    root.dataset.casesReady = "true";

    const track = root.querySelector("[data-cases-track]");
    const slides = Array.from(root.querySelectorAll("[data-cases-slide]"));
    const prevButton = root.querySelector("[data-cases-prev]");
    const nextButton = root.querySelector("[data-cases-next]");
    const counter = root.querySelector("[data-cases-counter]");
    const dotsRoot = root.querySelector("[data-cases-dots]");

    let index = 0;
    let pointerStartX = 0;
    let pointerDeltaX = 0;
    let isPointerDown = false;

    function total() {
      return slides.length;
    }

    function update() {
      if (!track || !total()) {
        return;
      }

      track.style.transform = `translate3d(-${index * 100}%, 0, 0)`;

      slides.forEach((slide, slideIndex) => {
        const isActive = slideIndex === index;
        slide.setAttribute("aria-hidden", isActive ? "false" : "true");
        slide.toggleAttribute("inert", !isActive);
      });

      if (counter) {
        counter.textContent = `${index + 1} / ${total()}`;
      }

      if (prevButton) {
        prevButton.disabled = index <= 0;
      }

      if (nextButton) {
        nextButton.disabled = index >= total() - 1;
      }

      if (dotsRoot) {
        dotsRoot.querySelectorAll("[data-cases-dot]").forEach((dot) => {
          const dotIndex = Number(dot.getAttribute("data-cases-dot"));
          const isActive = dotIndex === index;
          dot.classList.toggle("is-active", isActive);
          dot.setAttribute("aria-current", isActive ? "true" : "false");
        });
      }
    }

    function goTo(nextIndex) {
      if (!total()) {
        return;
      }

      index = Math.max(0, Math.min(total() - 1, nextIndex));
      update();
    }

    if (dotsRoot && total()) {
      dotsRoot.innerHTML = "";

      slides.forEach((_, slideIndex) => {
        const dot = document.createElement("button");
        dot.type = "button";
        dot.className = "cases__dot";
        dot.setAttribute("data-cases-dot", String(slideIndex));
        dot.setAttribute("aria-label", `Кейс ${slideIndex + 1}`);
        dotsRoot.appendChild(dot);
      });

      dotsRoot.addEventListener("click", (event) => {
        const dot = event.target.closest("[data-cases-dot]");

        if (!dot || !dotsRoot.contains(dot)) {
          return;
        }

        goTo(Number(dot.getAttribute("data-cases-dot")));
      });
    }

    if (prevButton) {
      prevButton.addEventListener("click", () => goTo(index - 1));
    }

    if (nextButton) {
      nextButton.addEventListener("click", () => goTo(index + 1));
    }

    root.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        goTo(index - 1);
      }

      if (event.key === "ArrowRight") {
        event.preventDefault();
        goTo(index + 1);
      }
    });

    if (track) {
      track.addEventListener(
        "pointerdown",
        (event) => {
          if (event.pointerType === "mouse" && event.button !== 0) {
            return;
          }

          isPointerDown = true;
          pointerStartX = event.clientX;
          pointerDeltaX = 0;
          track.setPointerCapture?.(event.pointerId);
        },
        { passive: true },
      );

      track.addEventListener(
        "pointermove",
        (event) => {
          if (!isPointerDown) {
            return;
          }

          pointerDeltaX = event.clientX - pointerStartX;
        },
        { passive: true },
      );

      const endPointer = () => {
        if (!isPointerDown) {
          return;
        }

        isPointerDown = false;

        if (Math.abs(pointerDeltaX) < 50) {
          return;
        }

        if (pointerDeltaX < 0) {
          goTo(index + 1);
        } else {
          goTo(index - 1);
        }
      };

      track.addEventListener("pointerup", endPointer);
      track.addEventListener("pointercancel", endPointer);
    }

    update();
  }

  function init() {
    document.querySelectorAll("[data-cases]").forEach(initSlider);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
