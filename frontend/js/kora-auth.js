
/**
 * kora-auth.js
 * Enlaza los formularios de login y registro con el API Gateway.
 */
(function () {
  "use strict";

  function showMessage(el, text, type) {
    if (!el) return;

    el.textContent = text;
    el.className = "mensaje-formulario";

    if (type) {
      el.classList.add("is-" + type);
    }
  }

  function setLoading(button, isLoading, loadingText, defaultText) {
    if (!button) return;

    button.disabled = isLoading;

    var buttonText = button.querySelector(".button-text");

    if (buttonText) {
      buttonText.textContent = isLoading ? loadingText : defaultText;
    }
  }

  function getRegistrationErrorMessage(error) {
    if (!error) {
      return "No se pudo completar el registro. Inténtalo nuevamente.";
    }

    if (error.code === "connection_error") return error.message;
    if (error.status === 400) return "No fue posible registrar la cuenta con los datos proporcionados.";
    if (error.status === 429) return "Se realizaron demasiados intentos. Inténtalo nuevamente más tarde.";
    if (error.status >= 500) return "El servicio no está disponible temporalmente. Inténtalo nuevamente más tarde.";

    return "No se pudo completar el registro. Inténtalo nuevamente.";
  }

  function getLoginErrorMessage(error) {
    if (!error) {
      return "No se pudo iniciar sesión. Inténtalo nuevamente.";
    }

    if (error.code === "connection_error") return error.message;
    if (error.status === 400) return "Los datos de acceso no son válidos.";
    if (error.status === 401) return "Correo o contraseña incorrectos.";
    if (error.status === 429) return "Se realizaron demasiados intentos. Inténtalo nuevamente más tarde.";
    if (error.status >= 500) return "El servicio no está disponible temporalmente. Inténtalo nuevamente más tarde.";

    return "No se pudo iniciar sesión. Inténtalo nuevamente.";
  }

  // Registro
  var regForm = document.getElementById("registrationForm");

  if (regForm) {
    regForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      var msg = document.getElementById("registrationMessage");
      var button = document.getElementById("registrationButton");

      var firstName = (document.getElementById("firstNameInput") || {}).value || "";
      var lastName = (document.getElementById("lastNameInput") || {}).value || "";
      var dateOfBirth = (document.getElementById("dateOfBirthInput") || {}).value || "";
      var email = (document.getElementById("emailInput") || {}).value || "";
      var password = (document.getElementById("passwordInput") || {}).value || "";
      var confirm = (document.getElementById("confirmPasswordInput") || {}).value || "";

      if (!regForm.checkValidity()) {
        regForm.reportValidity();
        showMessage(msg, "Completa correctamente todos los campos obligatorios.", "error");
        return;
      }

      if (!firstName.trim() || !lastName.trim() || !email.trim() || !dateOfBirth || !password) {
        showMessage(msg, "Completa todos los campos obligatorios.", "error");
        return;
      }

      if (password.length < 8) {
        showMessage(msg, "La contraseña debe contener al menos 8 caracteres.", "error");
        return;
      }

      if (password !== confirm) {
        showMessage(msg, "Las contraseñas no coinciden.", "error");
        return;
      }

      showMessage(msg, "Creando cuenta...", "info");
      setLoading(button, true, "Creando cuenta...", "Crear cuenta");

      try {
        var result = await KoraApi.registerUser({
          email: email.trim(),
          password: password,
          first_name: firstName.trim(),
          last_name: lastName.trim(),
          date_of_birth: dateOfBirth
        });

        var userData = (result && result.data) || result;

        if (userData && userData.user) {
          userData = userData.user;
        }

        KoraApi.setSession(userData, null, null);

        showMessage(msg, "Cuenta creada correctamente. Redirigiendo...", "success");

        setTimeout(function () {
          window.location.href = "initial_setup.html";
        }, 800);

      } catch (error) {
        showMessage(msg, getRegistrationErrorMessage(error), "error");
        setLoading(button, false, "Creando cuenta...", "Crear cuenta");
      }
    });
  }

  // Inicio de sesión
  var loginForm = document.getElementById("loginForm");

  if (loginForm && !document.getElementById("firstNameInput")) {
    loginForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      var msg = document.getElementById("loginMessage");
      var button = document.getElementById("loginButton");

      var email = (document.getElementById("emailInput") || {}).value || "";
      var password = (document.getElementById("passwordInput") || {}).value || "";

      if (!loginForm.checkValidity()) {
        loginForm.reportValidity();
        showMessage(msg, "Completa correctamente tus credenciales.", "error");
        return;
      }

      if (!email.trim() || !password) {
        showMessage(msg, "Ingresa correo y contraseña.", "error");
        return;
      }

      showMessage(msg, "Iniciando sesión...", "info");
      setLoading(button, true, "Iniciando sesión...", "Entrar a Kora");

      try {
        var result = await KoraApi.loginUser(email.trim(), password);
        var session = (result && result.data) || result;

        if (
          !session ||
          !session.access ||
          !session.refresh
        ) {
          throw new Error("La respuesta de autenticación no es válida.");
        }

        KoraApi.setSession(
          {
            user_id: session.user_id
          },
          session.access,
          session.refresh
        );

        showMessage(msg, "Sesión iniciada. Redirigiendo...", "success");

        setTimeout(function () {
          window.location.href = "app/main_panel.html";
        }, 600);

      } catch (error) {
        showMessage(msg, getLoginErrorMessage(error), "error");
        setLoading(button, false, "Iniciando sesión...", "Entrar a Kora");
      }
    });
  }

  // Cerrar sesión desde los enlaces
  document.querySelectorAll('a[href$="login.html"]').forEach(function (a) {
    if (/cerrar sesión/i.test(a.textContent || "")) {
      a.addEventListener("click", function () {
        if (window.KoraApi) {
          KoraApi.clearSession();
        }
      });
    }
  });

})();
