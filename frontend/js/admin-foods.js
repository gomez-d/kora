(function () {
    "use strict";

    const api = window.KoraApi;

    if (!api) {
        console.error("KoraApi no está cargado.");
        return;
    }
    const modal = document.getElementById("food-form-modal");
    const form = document.getElementById("food-form");
    const tbody = document.getElementById("foods-tbody");
    const openButton = document.getElementById("btn-open-food-form");
    const categorySelect = document.getElementById("food-category");
    const formTitle = document.getElementById("food-form-title");

    if (!api || !modal || !form || !tbody || !categorySelect) {
        console.error("The food administration interface is incomplete.");
        return;
    }

    let foods = [];
    let categories = [];

    function normalizeList(data) {
        if (Array.isArray(data)) return data;
        if (Array.isArray(data?.results)) return data.results;
        return [];
    }

    function getNutrient(food, type) {
        const nutrient = (food.nutrients || []).find(
            item => item.nutrient_type === type
        );

        return nutrient ? Number(nutrient.amount) : 0;
    }

    function openModal() {
        form.reset();
        formTitle.textContent = "Registrar alimento";
        modal.hidden = false;
        modal.classList.add("is-open");
    }

    function closeModal() {
        modal.classList.remove("is-open");

        window.setTimeout(() => {
            modal.hidden = true;
        }, 200);
    }

    function showError(error) {
    const message = error.message || "No se pudo completar la operación.";

    if (window.KoraAlerts) {
        window.KoraAlerts.error(message);
    } else {
        console.error(message);
    }
    
}

    async function loadCategories() {
        categorySelect.innerHTML =
            '<option value="">Cargando categorías...</option>';

        try {
                categories = normalizeList(
                    await api.listFoodCategories()
                );

            categorySelect.innerHTML =
                '<option value="">Seleccionar categoría...</option>';

            categories.forEach(category => {
                const option = document.createElement("option");
                option.value = category.id;
                option.textContent = category.name;
                categorySelect.appendChild(option);
            });

            if (categories.length === 0) {
                categorySelect.innerHTML =
                    '<option value="">No hay categorías registradas</option>';
            }
        } catch (error) {
            categorySelect.innerHTML =
                '<option value="">Error al cargar categorías</option>';
            showError(error);
        }
    }

    function renderFoods() {
        const query = (
            document.getElementById("food-search").value || ""
        ).trim().toLowerCase();

        const categoryFilter =
            document.getElementById("food-filter-category").value;

        tbody.replaceChildren();

        const filteredFoods = foods.filter(food => {
            const nameMatches = food.name.toLowerCase().includes(query);

            const categoryMatches =
                !categoryFilter ||
                food.category?.name?.toLowerCase() ===
                    categoryFilter.toLowerCase();

            return nameMatches && categoryMatches;
        });

        if (filteredFoods.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 9;
            cell.textContent = "No se encontraron alimentos.";
            row.appendChild(cell);
            tbody.appendChild(row);
            return;
        }

        filteredFoods.forEach(food => {
            const row = document.createElement("tr");

            const values = [
                food.name,
                food.category?.name || "Sin categoría",
                `${food.serving_size} ${food.serving_unit}`,
                `${getNutrient(food, "CALORIES")} kcal`,
                `${getNutrient(food, "PROTEIN")} g`,
                `${getNutrient(food, "CARBOHYDRATES")} g`,
                `${getNutrient(food, "FAT")} g`
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            const statusCell = document.createElement("td");
            statusCell.textContent = "Activo";
            row.appendChild(statusCell);

            const actionsCell = document.createElement("td");
            actionsCell.className = "actions";

            const viewButton = document.createElement("button");
            viewButton.type = "button";
            viewButton.className =
                "admin-btn admin-btn--ghost admin-btn--sm";
            viewButton.textContent = "Ver";
            viewButton.addEventListener("click", () => {
                window.KoraAlerts.error(
                    `${food.name}\n` +
                    `Descripción: ${food.description}\n` +
                    `Porción: ${food.serving_size} ${food.serving_unit}`
                );
            });

            actionsCell.appendChild(viewButton);
            row.appendChild(actionsCell);
            tbody.appendChild(row);
        });
    }

    async function loadFoods() {
        try {
            foods = normalizeList(
                await api.listFoods()
            );
            renderFoods();
        } catch (error) {
            showError(error);
        }
    }

    function buildNutrients() {
        return [
            {
                nutrient_type: "CALORIES",
                amount: document.getElementById("food-calories").value,
                unit: "KCAL"
            },
            {
                nutrient_type: "PROTEIN",
                amount: document.getElementById("food-protein").value,
                unit: "G"
            },
            {
                nutrient_type: "CARBOHYDRATES",
                amount: document.getElementById("food-carbs").value,
                unit: "G"
            },
            {
                nutrient_type: "FAT",
                amount: document.getElementById("food-fat").value,
                unit: "G"
            },
            {
                nutrient_type: "FIBER",
                amount: document.getElementById("food-fiber").value,
                unit: "G"
            },
            {
                nutrient_type: "SUGAR",
                amount: document.getElementById("food-sugar").value,
                unit: "G"
            },
            {
                nutrient_type: "SODIUM",
                amount: document.getElementById("food-sodium").value,
                unit: "MG"
            }
        ];
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();

        if (!form.reportValidity()) return;

        const name = document.getElementById("food-name").value.trim();
        const description =
            document.getElementById("food-description").value.trim();

        const servingSize = Number(
            document.getElementById("food-portion-size").value
        );

        if (!name || !description || servingSize <= 0) {
            window.KoraAlerts.error(
                "Completa los campos obligatorios correctamente."
            );
            return;
        }

        const submitButton = form.querySelector('[type="submit"]');
        submitButton.disabled = true;

        try {
            const payload = {
                category_id: categorySelect.value,
                name: name,
                description: description,
                serving_size: servingSize,
                serving_unit: document.getElementById(
                    "food-portion-unit"
                ).value,
                nutrients: buildNutrients()
            };

            await api.createFood(payload);

            closeModal();
            await loadFoods();

            window.KoraAlerts.success("Alimento registrado correctamente.");
        } catch (error) {
            showError(error);
        } finally {
            submitButton.disabled = false;
        }
    });

    if (openButton) {
        openButton.addEventListener("click", openModal);
    }

    modal.querySelectorAll("[data-close-modal]").forEach(element => {
        element.addEventListener("click", closeModal);
    });

    ["food-search", "food-filter-category"].forEach(id => {
        const element = document.getElementById(id);

        if (element) {
            element.addEventListener("input", renderFoods);
            element.addEventListener("change", renderFoods);
        }
    });

    // This model does not currently support active/inactive status.
    const statusFilter = document.getElementById("food-filter-status");

    if (statusFilter) {
        statusFilter.disabled = true;
        statusFilter.title =
            "El estado de los alimentos aún no está implementado en el backend.";
    }

    Promise.all([loadCategories(), loadFoods()]);
})();
