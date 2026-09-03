export function initPartners() {
  const button = document.querySelector("[data-partners-more]");
  const list = document.querySelector("[data-partners-list]");
  const tiles = document.querySelectorAll("[data-partners-flip]");

  if (button && list) {
    button.addEventListener("click", () => {
      list.classList.add("partners__list--expanded");
      button.hidden = true;
    });
  }

  if (!tiles.length) {
    return;
  }

  const prefersFineHover = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  tiles.forEach((tile) => {
    tile.setAttribute("role", "button");
    tile.setAttribute("aria-label", "Показать кейс партнёра");
  });

  if (prefersFineHover) {
    return;
  }

  const setFlipped = (tile, flipped) => {
    tile.classList.toggle("is-flipped", flipped);
    const back = tile.querySelector(".partners__face--back");
    if (back) {
      back.setAttribute("aria-hidden", flipped ? "false" : "true");
    }
  };

  const closeOthers = (current) => {
    tiles.forEach((tile) => {
      if (tile !== current) {
        setFlipped(tile, false);
      }
    });
  };

  tiles.forEach((tile) => {
    tile.addEventListener("click", (event) => {
      event.preventDefault();
      const willFlip = !tile.classList.contains("is-flipped");
      closeOthers(tile);
      setFlipped(tile, willFlip);
    });

    tile.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") {
        return;
      }

      event.preventDefault();
      const willFlip = !tile.classList.contains("is-flipped");
      closeOthers(tile);
      setFlipped(tile, willFlip);
    });
  });

  document.addEventListener("click", (event) => {
    if (event.target.closest("[data-partners-flip]")) {
      return;
    }

    tiles.forEach((tile) => setFlipped(tile, false));
  });
}
