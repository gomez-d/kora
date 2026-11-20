/**
 * kora-auth.js
 * Enlaza formularios de login.html y registration.html con el API Gateway.
 */
(function () {
  "use strict";

  function showMessage(el, text, isError) {
    if (!el) return;
    el.textContent = text;
    el.style.display = "block";
    el.style.color = isError ? "#b00020" : "#2e7d32";
  }

  function ensureMessageBox(form) {
    var id = "kora-form-message";
    var box = document.getElementById(id);
    if (!box) {
      box = document.createElement("div");
      box.id = id;
      box.setAttribute("role", "alert");
      box.style.margin = "0.75rem 0";
      box.style.fontSize = "0.95rem";
      form.insertBefore(box, form.firstChild);
    }
    return box;
  }

  // ---- Registro ----
  var regForm = document.getElementById("registrationForm") || document.getElementById("loginForm");
  if (regForm && document.getElementById("firstNameInput")) {
    regForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      var msg = ensureMessageBox(regForm);
      var first_name = (document.getElementById("firstNameInput") || {}).value || "";
      var last_name = (document.getElementById("lastNameInput") || {}).value || "";
      var username = (document.getElementById("usernameInput") || {}).value || "";
      var email = (document.getElementById("emailInput") || {}).value || "";
      var password = (document.getElementById("passwordInput") || {}).value || "";
      var confirm = (document.getElementById("confirmPasswordInput") || {}).value || "";

      if (!username || !email || !password || !first_name || !last_name) {
        showMessage(msg, "Completa todos los campos obligatorios.", true);
        return;
      }
      if (password !== confirm) {
        showMessage(msg, "Las contraseñas no coinciden.", true);
        return;
      }

      showMessage(msg, "Creando cuenta…", false);
      try {
        var result = await KoraApi.registerUser({
          username: username.trim(),
          email: email.trim(),
          password: password,
          first_name: first_name.trim(),
          last_name: last_name.trim()
        });
        var userData = (result && result.data) || result;
        KoraApi.setSession(userData, null);
        showMessage(msg, "Cuenta creada correctamente. Redirigiendo…", false);
        setTimeout(function () {
          window.location.href = "initial_setup.html";
        }, 800);
      } catch (err) {
        var detail = err.message || "No se pudo registrar.";
        if (err.data && err.data.errors) {
          detail = JSON.stringify(err.data.errors);
        }
        showMessage(msg, detail, true);
      }
    });
  }

  // ---- Login ----
  var loginForm = document.getElementById("loginForm");
  if (loginForm && !document.getElementById("firstNameInput") && document.getElementById("emailInput")) {
    // Evitar que el enlace "Entrar" navegue sin enviar
    var enterLink = loginForm.querySelector('a.btn');
    if (enterLink) {
      enterLink.addEventListener("click", function (e) {
        e.preventDefault();
        loginForm.requestSubmit ? loginForm.requestSubmit() : loginForm.dispatchEvent(new Event("submit", { cancelable: true }));
      });
    }

    loginForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      var msg = ensureMessageBox(loginForm);
      var email = (document.getElementById("emailInput") || {}).value || "";
      var password = (document.getElementById("passwordInput") || {}).value || "";
      if (!email || !password) {
        showMessage(msg, "Ingresa correo y contraseña.", true);
        return;
      }
      showMessage(msg, "Iniciando sesión…", false);
      try {
        var result = await KoraApi.loginUser(email.trim(), password);
        var userData = (result && result.data) || result;
        KoraApi.setSession(userData, (result && result.token) || null);
        showMessage(msg, "Sesión iniciada. Redirigiendo…", false);
        setTimeout(function () {
          window.location.href = "app/main_panel.html";
        }, 600);
      } catch (err) {
        // Si no hay login en backend, permitir acceso demo solo en desarrollo
        showMessage(msg, err.message || "No se pudo iniciar sesión.", true);
      }
    });
  }

  // ---- Cerrar sesión (enlaces) ----
  document.querySelectorAll('a[href$="login.html"]').forEach(function (a) {
    if (/cerrar sesión/i.test(a.textContent || "")) {
      a.addEventListener("click", function () {
        if (window.KoraApi) KoraApi.clearSession();
      });
    }
  });
})();
