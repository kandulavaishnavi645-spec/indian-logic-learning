(() => {
    const menuToggle = document.querySelector(".menu-toggle");
    const navigation = document.querySelector("#primary-navigation");

    if (menuToggle && navigation) {
        menuToggle.addEventListener("click", () => {
            const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
            menuToggle.setAttribute("aria-expanded", String(!isOpen));
            menuToggle.setAttribute("aria-label", isOpen ? "Open navigation" : "Close navigation");
            navigation.classList.toggle("is-open", !isOpen);
        });

        navigation.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                menuToggle.setAttribute("aria-expanded", "false");
                menuToggle.setAttribute("aria-label", "Open navigation");
                navigation.classList.remove("is-open");
            });
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                menuToggle.setAttribute("aria-expanded", "false");
                menuToggle.setAttribute("aria-label", "Open navigation");
                navigation.classList.remove("is-open");
            }
        });
    }

    document.querySelectorAll(".product-image img, .detail-art img, .cart-thumb img").forEach((image) => {
        image.addEventListener("error", () => {
            image.hidden = true;
        }, { once: true });
    });

    const productGrid = document.querySelector("#product-grid");
    const sortSelect = document.querySelector("#sort-products");
    if (productGrid && sortSelect) {
        const cards = Array.from(productGrid.querySelectorAll(".product-card"));
        cards.forEach((card, index) => {
            card.dataset.originalOrder = String(index);
        });

        sortSelect.addEventListener("change", () => {
            const sortBy = sortSelect.value;
            const sortedCards = [...cards].sort((first, second) => {
                if (sortBy === "price-low" || sortBy === "price-high") {
                    const difference = Number(first.dataset.price) - Number(second.dataset.price);
                    return sortBy === "price-low" ? difference : -difference;
                }
                if (sortBy === "name") {
                    return first.dataset.name.localeCompare(second.dataset.name);
                }
                return Number(first.dataset.originalOrder) - Number(second.dataset.originalOrder);
            });

            sortedCards.forEach((card) => productGrid.appendChild(card));
        });
    }
})();
