
(function (global) {
    "use strict";

    var api = global.KoraApi;

    function isAuthenticated() {
        return Boolean(
            api &&
            api.getToken() &&
            api.getRefreshToken()
        );
    }

    function getUser() {
        return api ? api.getUser() : null;
    }

    async function requireAuth() {
        if (!api) {
            window.location.replace("../login.html");
            return false;
        }

        try {
            var valid = await api.ensureAccessToken();

            if (!valid) {
                api.clearSession();
                window.location.replace("../login.html");
                return false;
            }

            // Mostrar la página cuando la sesión es válida.
            document.documentElement.style.visibility = "visible";

            return true;

        } catch (error) {
            console.error("Error al validar la sesión:", error);

            api.clearSession();
            window.location.replace("../login.html");
            return false;
        }
    }

    async function logout() {
        try {
            await api.logout();
        } finally {
            window.location.replace("../login.html");
        }
    }

    document.addEventListener("click", function (event) {
        var button = event.target.closest("#kora-logout");

        if (!button) {
            return;
        }

        event.preventDefault();

        button.textContent = "Cerrando sesión...";
        button.style.pointerEvents = "none";

        logout();
    });

    global.KoraSession = {
        isAuthenticated: isAuthenticated,
        getUser: getUser,
        requireAuth: requireAuth,
        logout: logout
    };

})(window);
