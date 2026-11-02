(() => {
    const page = document.querySelector(".account-page");
    const card = document.querySelector(".account-card");
    if (!page || !card) {
        return;
    }

    const supports3dPointer = window.matchMedia(
        "(min-width: 681px) and (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)"
    );
    if (!supports3dPointer.matches) {
        return;
    }

    page.addEventListener("pointermove", (event) => {
        const bounds = page.getBoundingClientRect();
        const x = (event.clientX - bounds.left) / bounds.width - 0.5;
        const y = (event.clientY - bounds.top) / bounds.height - 0.5;
        card.style.setProperty("--card-y", `${x * 9}deg`);
        card.style.setProperty("--card-x", `${y * -7}deg`);
        card.style.setProperty("--card-lift", "-5px");
        page.style.setProperty("--pointer-x", `${event.clientX}px`);
        page.style.setProperty("--pointer-y", `${event.clientY}px`);
    });

    page.addEventListener("pointerleave", () => {
        ["--card-y", "--card-x", "--card-lift"].forEach((property) => {
            card.style.removeProperty(property);
        });
        ["--pointer-x", "--pointer-y"].forEach((property) => {
            page.style.removeProperty(property);
        });
    });
})();
