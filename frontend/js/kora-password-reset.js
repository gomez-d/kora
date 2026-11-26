
/**
 * kora-password-reset.js
 * Handle password recovery forms through the API Gateway.
 */
(function () {
  "use strict";

  function showMessage(element, message, isError) {
    if (!element) return;

    element.textContent = message;
    element.hidden = false;
    element.style.display = "block";
    element.style.color = isError ? "#b00020" : "#2e7d32";
    element.setAttribute("role", isError ? "alert" : "status");
  }

  // ---- Password recovery request ----
  var forgotForm = document.getElementById("forgotPasswordForm");

  if (forgotForm) {
    var emailInput = document.getElementById("emailInput");
    var submitButton = document.getElementById("submitButton");
    var formMessage = document.getElementById("formMessage");

    forgotForm.addEventListener("submit", async function (event) {
      event.preventDefault();

      if (submitButton.disabled) return;

      var email = emailInput.value.trim();

      if (!email || !emailInput.checkValidity()) {
        showMessage(
          formMessage,
          "Ingresa un correo electrónico válido.",
          true
        );
        return;
      }

      submitButton.disabled = true;
      submitButton.textContent = "Enviando...";

      try {
        await KoraApi.requestPasswordReset(email);

        showMessage(
          formMessage,
          "Si el correo está registrado, recibirás instrucciones para recuperar tu contraseña.",
          false
        );

        forgotForm.reset();

      } catch (error) {
        var message = "No fue posible procesar la solicitud. Inténtalo nuevamente.";

        if (error.status === 429) {
          message = "Has realizado demasiadas solicitudes. Inténtalo más tarde.";
        } else if (error.status === 400) {
          message = "Verifica que el correo electrónico sea válido.";
        } else if (error.status >= 500) {
          message = "El servicio no está disponible temporalmente.";
        } else if (!error.status) {
          message = "No se pudo establecer conexión con el servidor.";
        }

        showMessage(formMessage, message, true);

      } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Enviar instrucciones";
      }
    });
  }

  
  // ---- Password reset confirmation ----
  var resetForm = document.getElementById("resetPasswordForm");

  if (resetForm) {
    var newPasswordInput = document.getElementById("newPasswordInput");
    var confirmPasswordInput = document.getElementById("confirmPasswordInput");
    var resetSubmitButton = document.getElementById("resetSubmitButton");
    var resetFormMessage = document.getElementById("resetFormMessage");

    // Retrieve the recovery token from the URL.
    var params = new URLSearchParams(window.location.search);
    var recoveryToken = params.get("token");

    // Remove the token from the visible URL and browser history.
    if (recoveryToken) {
      window.history.replaceState(
        null,
        "",
        window.location.pathname
      );
    }

    if (!recoveryToken) {
      showMessage(
        resetFormMessage,
        "El enlace de recuperación no es válido o está incompleto.",
        true
      );

      resetSubmitButton.disabled = true;
    }

    resetForm.addEventListener("submit", async function (event) {
      event.preventDefault();

      if (resetSubmitButton.disabled || !recoveryToken) {
        return;
      }

      var newPassword = newPasswordInput.value;
      var confirmPassword = confirmPasswordInput.value;

      if (!newPasswordInput.checkValidity()) {
        showMessage(
          resetFormMessage,
          "La contraseña debe tener al menos 8 caracteres.",
          true
        );
        return;
      }

      if (newPassword !== confirmPassword) {
        showMessage(
          resetFormMessage,
          "Las contraseñas no coinciden.",
          true
        );
        return;
      }

      resetSubmitButton.disabled = true;
      resetSubmitButton.textContent = "Restableciendo...";

      try {
        await KoraApi.confirmPasswordReset(
          recoveryToken,
          newPassword
        );

        recoveryToken = null;
        resetForm.reset();

        showMessage(
          resetFormMessage,
          "Tu contraseña se restableció correctamente. Ya puedes iniciar sesión.",
          false
        );

        resetSubmitButton.textContent = "Contraseña actualizada";

      } catch (error) {
        var message = "No fue posible restablecer la contraseña.";

        if (error.status === 400) {
          message = "El enlace es inválido, ha expirado o la contraseña no cumple los requisitos.";
        } else if (error.status === 429) {
          message = "Demasiados intentos. Inténtalo nuevamente más tarde.";
        } else if (error.status >= 500) {
          message = "El servicio no está disponible temporalmente.";
        } else if (!error.status) {
          message = "No se pudo establecer conexión con el servidor.";
        }

        showMessage(resetFormMessage, message, true);

        resetSubmitButton.disabled = false;
        resetSubmitButton.textContent = "Restablecer contraseña";
      }
    });
  }

})();
