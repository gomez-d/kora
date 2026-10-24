
(function () {
    function showAlert(message, type = "info") {
        const container = document.getElementById("kora-alerts");

        if (!container) {
            console.error("No se encontró el contenedor de alertas.");
            return;
        }

        const allowedTypes = ["success", "error", "info", "notice"];
        const alertType = allowedTypes.includes(type) ? type : "info";

        const alert = document.createElement("div");
        alert.className = `alert-box alert-box--${alertType}`;

        const paragraph = document.createElement("p");
        paragraph.textContent = message;

        const closeButton = document.createElement("button");
        closeButton.type = "button";
        closeButton.className = "alert-box__close";
        closeButton.setAttribute("aria-label", "Cerrar mensaje");

        closeButton.addEventListener("click", function () {
            alert.remove();
        });

        alert.appendChild(paragraph);
        alert.appendChild(closeButton);
        container.appendChild(alert);

        // Automatically remove the alert after 3 seconds.
        window.setTimeout(function () {
            alert.remove();
        }, 3000);
    }

    window.KoraAlerts = {
        success: (message) => showAlert(message, "success"),
        error: (message) => showAlert(message, "error"),
        info: (message) => showAlert(message, "info"),
        notice: (message) => showAlert(message, "notice")
    };
})();
