(function () {
    "use strict";

    const grid = document.getElementById("catalog-grid");
    const emptyEl = document.getElementById("catalog-empty");
    const emptyMessage = document.getElementById("catalog-empty-message");
    const loadingEl = document.getElementById("catalog-loading");
    const statusEl = document.getElementById("catalog-status");
    const searchInput = document.getElementById("catalog-search");
    const btnSearch = document.getElementById("btn-search");
    const sortSelect = document.getElementById("catalog-sort");
    const modal = document.getElementById("food-detail-modal");

    let foods = [];
    let currentFood = null;

    const NUTRIENT_LABELS = {
        CALORIES: "Calorías",
        CALORIE: "Calorías",
        ENERGY: "Energía",
        KCAL: "Calorías",
        PROTEIN: "Proteína",
        PROTEINS: "Proteína",
        CARBOHYDRATES: "Carbohidratos",
        CARBOHYDRATE: "Carbohidratos",
        CARBS: "Carbohidratos",
        FAT: "Grasas",
        TOTAL_FAT: "Grasas totales",
        TOTAL_FATS: "Grasas totales",
        FIBER: "Fibra",
        DIETARY_FIBER: "Fibra",
        SUGAR: "Azúcar",
        SUGARS: "Azúcares",
        SODIUM: "Sodio",
        CHOLESTEROL: "Colesterol",
        SATURATED_FAT: "Grasas saturadas"
    };

    function formatNum(value) {
        if (value === null || value === undefined || value === "") return "—";
        const number = Number(value);
        return Number.isFinite(number)
            ? (number % 1 === 0
                ? String(number)
                : number.toFixed(2).replace(/0+$/, "").replace(/\.$/, ""))
            : "—";
    }

    function normalizeNutrientType(type) {
        return String(type || "").trim().toUpperCase().replace(/[\s-]+/g, "_");
    }

    function getNutrients(food) {
        return Array.isArray(food.nutrients) ? food.nutrients : [];
    }

    function nutrientValue(food, possibleTypes) {
        const nutrient = getNutrients(food).find(function (item) {
            return possibleTypes.includes(normalizeNutrientType(item.nutrient_type));
        });
        return nutrient ? Number(nutrient.amount) : null;
    }

    function getCalories(food) {
        return nutrientValue(food, ["CALORIES", "CALORIE", "ENERGY", "KCAL"]);
    }

    function getProtein(food) {
        return nutrientValue(food, ["PROTEIN", "PROTEINS"]);
    }

    function getCarbohydrates(food) {
        return nutrientValue(food, ["CARBOHYDRATES", "CARBOHYDRATE", "CARBS"]);
    }

    function getFat(food) {
        return nutrientValue(food, ["FAT", "TOTAL_FAT", "TOTAL_FATS"]);
    }

    function getNutrientLabel(type) {
        const normalized = normalizeNutrientType(type);
        return NUTRIENT_LABELS[normalized] ||
            String(type || "Nutriente").replace(/_/g, " ");
    }

    function getFoodId(food) {
        return food.id || food.food_id || "";
    }

    function setStatus(message, isError) {
        statusEl.textContent = message || "";
        statusEl.style.color = isError ? "#b42318" : "";
    }

    function showEmpty(message) {
        grid.innerHTML = "";
        emptyMessage.textContent = message;
        emptyEl.style.display = "block";
    }

    function renderCards(list) {
        grid.innerHTML = "";

        if (!list.length) {
            showEmpty("No se encontraron alimentos con ese criterio.");
            return;
        }

        emptyEl.style.display = "none";

        list.forEach(function (food) {
            const card = document.createElement("article");
            card.className = "s-catalog__card";

            const name = document.createElement("h3");
            name.className = "s-catalog__card-title";
            name.textContent = food.name || "Alimento sin nombre";

            const macros = document.createElement("div");
            macros.className = "s-catalog__card-macros";

            [
                ["Calorías", getCalories(food), "kcal"],
                ["Proteína", getProtein(food), "g"],
                ["Carbohidratos", getCarbohydrates(food), "g"],
                ["Grasas", getFat(food), "g"]
            ].forEach(function (item) {
                const span = document.createElement("span");
                span.textContent = item[0] + ": " + formatNum(item[1]) +
                    (item[1] === null ? "" : " " + item[2]);
                macros.appendChild(span);
            });

            const actions = document.createElement("div");
            actions.className = "s-catalog__card-actions";

            const detailButton = document.createElement("button");
            detailButton.type = "button";
            detailButton.className =
                "s-alimento__btn s-alimento__btn--secondary s-catalog__btn-detail";
            detailButton.textContent = "Ver detalles";
            detailButton.addEventListener("click", function () {
                openDetail(food);
            });

            const registerLink = document.createElement("a");
            registerLink.href = "food_intake.html?food_id=" +
                encodeURIComponent(getFoodId(food)) +
                "&name=" + encodeURIComponent(food.name || "");
            registerLink.className = "s-alimento__btn s-alimento__btn--primary";
            registerLink.textContent = "Registrar";

            actions.appendChild(detailButton);
            actions.appendChild(registerLink);
            card.appendChild(name);
            card.appendChild(macros);
            card.appendChild(actions);
            grid.appendChild(card);
        });
    }

    function openDetail(food) {
        currentFood = food;
        document.getElementById("food-detail-title").textContent = food.name || "—";

        const size = food.serving_size;
        const unit = food.serving_unit || "";
        document.getElementById("food-detail-portion").textContent =
            "Porción de referencia: " + (size == null ? "—" : formatNum(size)) +
            (unit ? " " + unit : "");

        document.getElementById("food-detail-description").textContent =
            food.description || "Sin descripción disponible.";

        const category = food.category;
        document.getElementById("food-detail-category").textContent =
            "Categoría: " + (category && typeof category === "object"
                ? (category.name || "Sin categoría")
                : (category || "Sin categoría"));

        const nutrientsContainer = document.getElementById("food-detail-nutrients");
        nutrientsContainer.innerHTML = "";
        const nutrients = getNutrients(food);

        if (!nutrients.length) {
            const message = document.createElement("p");
            message.textContent = "Este alimento no tiene nutrientes registrados.";
            nutrientsContainer.appendChild(message);
        } else {
            nutrients.forEach(function (nutrient) {
                const item = document.createElement("div");
                item.className = "kora-modal__nutrient";

                const label = document.createElement("span");
                label.textContent = getNutrientLabel(nutrient.nutrient_type);

                const amount = document.createElement("strong");
                amount.textContent = formatNum(nutrient.amount);

                const unitLabel = document.createElement("small");
                unitLabel.textContent = nutrient.unit || "";

                item.appendChild(label);
                item.appendChild(amount);
                item.appendChild(unitLabel);
                nutrientsContainer.appendChild(item);
            });
        }

        const imageWrap = document.getElementById("food-detail-image-wrap");
        const image = document.getElementById("food-detail-image");
        if (food.image) {
            image.src = food.image;
            image.alt = food.name || "Alimento";
            imageWrap.style.display = "block";
        } else {
            image.removeAttribute("src");
            image.alt = "";
            imageWrap.style.display = "none";
        }

        document.getElementById("food-detail-register-btn").href =
            "food_intake.html?food_id=" + encodeURIComponent(getFoodId(food)) +
            "&name=" + encodeURIComponent(food.name || "");

        modal.classList.add("is-open");
        modal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
    }

    function closeModal() {
        modal.classList.remove("is-open");
        modal.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
        currentFood = null;
    }

    modal.querySelectorAll("[data-close-modal]").forEach(function (element) {
        element.addEventListener("click", closeModal);
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && modal.classList.contains("is-open")) {
            closeModal();
        }
    });

    function filterAndSort() {
        const query = (searchInput.value || "").trim().toLocaleLowerCase("es");
        let filtered = foods.filter(function (food) {
            return String(food.name || "").toLocaleLowerCase("es").includes(query);
        });

        const sort = sortSelect.value;
        filtered.sort(function (a, b) {
            if (sort === "name") {
                return String(a.name || "").localeCompare(String(b.name || ""), "es");
            }

            const getters = {
                calories: getCalories,
                protein: getProtein
            };
            const getter = getters[sort];
            return getter
                ? (Number(getter(b) ?? -1) - Number(getter(a) ?? -1))
                : 0;
        });

        renderCards(filtered);
        setStatus(filtered.length +
            (filtered.length === 1 ? " alimento encontrado." : " alimentos encontrados."));
    }

    btnSearch.addEventListener("click", filterAndSort);

    searchInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            filterAndSort();
        }
    });

    sortSelect.addEventListener("change", filterAndSort);

    async function loadFromApi() {
        loadingEl.style.display = "block";
        emptyEl.style.display = "none";
        grid.innerHTML = "";
        setStatus("Consultando el catálogo…");

        try {
            if (!window.KoraApi || typeof window.KoraApi.listFoods !== "function") {
                throw new Error(
                    "No se encontró KoraApi.listFoods(). Verifica que kora-api.js esté cargado."
                );
            }

            const response = await window.KoraApi.listFoods();
            const list = Array.isArray(response)
                ? response
                : (response && Array.isArray(response.results)
                    ? response.results
                    : (response && Array.isArray(response.data)
                        ? response.data
                        : null));

            if (!list) {
                throw new Error("La respuesta del catálogo no tiene el formato esperado.");
            }

            foods = list;
            loadingEl.style.display = "none";

            if (!foods.length) {
                showEmpty("El catálogo no contiene alimentos registrados.");
                setStatus("Consulta completada.");
                return;
            }

            filterAndSort();
        } catch (error) {
            loadingEl.style.display = "none";
            showEmpty(
                "No fue posible cargar el catálogo. Verifica que el API Gateway y svc-business estén activos."
            );
            setStatus(error.message || "Error al consultar los alimentos.", true);
            console.error("Error al consultar svc-business:", error);
        }
    }

    loadFromApi();
})();
