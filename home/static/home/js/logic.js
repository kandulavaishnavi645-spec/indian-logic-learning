(() => {
    const menuToggle = document.querySelector(".menu-toggle");
    const navigation = document.querySelector("#primary-navigation");

    const closeNavigation = () => {
        if (!menuToggle || !navigation) {
            return;
        }
        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "Open navigation");
        navigation.classList.remove("is-open");
    };

    if (menuToggle && navigation) {
        menuToggle.addEventListener("click", () => {
            const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
            menuToggle.setAttribute("aria-expanded", String(!isOpen));
            menuToggle.setAttribute("aria-label", isOpen ? "Open navigation" : "Close navigation");
            navigation.classList.toggle("is-open", !isOpen);
        });

        navigation.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", closeNavigation);
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                closeNavigation();
            }
        });
    }

    const quizTabs = Array.from(document.querySelectorAll(".quiz-tab"));
    const quizPanels = quizTabs
        .map((tab) => document.getElementById(tab.getAttribute("aria-controls")))
        .filter((panel) => panel);

    const activateQuizTab = (tab) => {
        if (tab.disabled) {
            return;
        }
        quizTabs.forEach((quizTab) => {
            const isActive = quizTab === tab;
            quizTab.classList.toggle("is-active", isActive);
            quizTab.setAttribute("aria-selected", String(isActive));
        });
        quizPanels.forEach((panel) => {
            panel.hidden = panel.id !== tab.getAttribute("aria-controls");
        });
        tab.focus();
    };

    quizTabs.forEach((tab, index) => {
        tab.addEventListener("click", () => activateQuizTab(tab));
        tab.addEventListener("keydown", (event) => {
            let nextIndex = index;
            if (event.key === "ArrowRight") {
                nextIndex = (index + 1) % quizTabs.length;
            } else if (event.key === "ArrowLeft") {
                nextIndex = (index - 1 + quizTabs.length) % quizTabs.length;
            } else if (event.key === "Home") {
                nextIndex = 0;
            } else if (event.key === "End") {
                nextIndex = quizTabs.length - 1;
            } else {
                return;
            }
            event.preventDefault();
            const nextTab = quizTabs[nextIndex];
            if (!nextTab.disabled) {
                activateQuizTab(nextTab);
            }
        });
    });

    const resultTab = document.querySelector("#quiz-result-tab");
    const restartButton = document.querySelector("[data-restart-quiz]");
    if (restartButton) {
        restartButton.addEventListener("click", () => {
            const resultPanel = document.querySelector("#quiz-result-panel");
            const mode = resultPanel ? resultPanel.dataset.quizMode : "multiple-choice";
            const tab = document.querySelector(`#${mode}-tab`);
            const form = document.querySelector(`#${mode}-panel form`);
            if (form) {
                form.querySelectorAll("input").forEach((input) => {
                    if (input.type === "radio" || input.type === "checkbox") {
                        input.checked = false;
                    } else if (input.type !== "hidden") {
                        input.value = "";
                    }
                });
            }
            if (resultTab) {
                resultTab.disabled = true;
            }
            if (tab) {
                activateQuizTab(tab);
            }
        });
    }

    const supports3dPointer = window.matchMedia(
        "(min-width: 561px) and (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)"
    );
    if (supports3dPointer.matches) {
        document.querySelectorAll(".philosophy-hero, .relation-hero").forEach((hero) => {
            const scene = hero.querySelector(".temple-art, .brain-art");
            if (!scene) {
                return;
            }
            hero.addEventListener("pointermove", (event) => {
                const bounds = hero.getBoundingClientRect();
                const x = ((event.clientX - bounds.left) / bounds.width - 0.5) * 2;
                const y = ((event.clientY - bounds.top) / bounds.height - 0.5) * 2;
                hero.style.setProperty("--light-x", `${((x + 1) / 2) * 100}%`);
                hero.style.setProperty("--light-y", `${((y + 1) / 2) * 100}%`);
                scene.style.setProperty("--scene-x", `${x * 12}px`);
                scene.style.setProperty("--scene-y", `${y * 10}px`);
                scene.style.setProperty("--scene-rotate-x", `${y * -10}deg`);
                scene.style.setProperty("--scene-rotate-y", `${x * 14}deg`);
                scene.style.setProperty("--brain-rotate-x", `${y * -20}deg`);
                scene.style.setProperty("--brain-rotate-y", `${x * 26}deg`);
            });
            hero.addEventListener("pointerleave", () => {
                ["--light-x", "--light-y"].forEach((property) => hero.style.removeProperty(property));
                ["--scene-x", "--scene-y", "--scene-rotate-x", "--scene-rotate-y", "--brain-rotate-x", "--brain-rotate-y"]
                    .forEach((property) => scene.style.removeProperty(property));
            });
        });

        document.querySelectorAll(
            ".system-card, .pramana-card, .ai-flow > article, .question-card, .argument-block li"
        ).forEach((card) => {
            card.addEventListener("pointermove", (event) => {
                const bounds = card.getBoundingClientRect();
                const x = (event.clientX - bounds.left) / bounds.width - 0.5;
                const y = (event.clientY - bounds.top) / bounds.height - 0.5;
                card.style.setProperty("--card-tilt-x", `${y * -11}deg`);
                card.style.setProperty("--card-tilt-y", `${x * 11}deg`);
                card.classList.add("is-pointer-active");
            });
            card.addEventListener("pointerleave", () => {
                card.style.removeProperty("--card-tilt-x");
                card.style.removeProperty("--card-tilt-y");
                card.classList.remove("is-pointer-active");
            });
        });
    }
})();
