
(function (global) {
  "use strict";

  function cfg() {
    return global.KoraConfig || {
      API_BASE: "http://localhost:8000",
      endpoints: {},
      storageKeys: {
        user: "kora_user",
        accessToken: "kora_access_token",
        refreshToken: "kora_refresh_token"
      }
    };
  }

  function url(path) {
    if (!path) return cfg().API_BASE;
    if (/^https?:\/\//i.test(path)) return path;

    return cfg().API_BASE +
      (path.charAt(0) === "/" ? path : "/" + path);
  }

  function getToken() {
    return sessionStorage.getItem(cfg().storageKeys.accessToken) || "";
  }

  function getRefreshToken() {
    return sessionStorage.getItem(cfg().storageKeys.refreshToken) || "";
  }

  function getUser() {
    try {
      var raw = sessionStorage.getItem(cfg().storageKeys.user);
      return raw ? JSON.parse(raw) : null;
    } catch (error) {
      return null;
    }
  }

  function setSession(user, accessToken, refreshToken) {
    if (user) {
      sessionStorage.setItem(
        cfg().storageKeys.user,
        JSON.stringify(user)
      );
    }

    if (accessToken) {
      sessionStorage.setItem(
        cfg().storageKeys.accessToken,
        accessToken
      );
    }

    if (refreshToken) {
      sessionStorage.setItem(
        cfg().storageKeys.refreshToken,
        refreshToken
      );
    }
  }

  function clearSession() {
    sessionStorage.removeItem(cfg().storageKeys.user);
    sessionStorage.removeItem(cfg().storageKeys.accessToken);
    sessionStorage.removeItem(cfg().storageKeys.refreshToken);
  }

  var refreshPromise = null;

  async function refreshSession() {
    if (refreshPromise) {
      return refreshPromise;
    }

    var refreshToken = getRefreshToken();

    if (!refreshToken) {
      clearSession();
      throw new Error("No existe refresh token.");
    }

    refreshPromise = (async function () {
      try {
        var response = await fetch(url(cfg().endpoints.refresh), {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            refresh: refreshToken
          })
        });

        var data = await response.json().catch(function () {
          return {};
        });

        if (!response.ok || !data.access) {
          throw new Error("No se pudo renovar la sesión.");
        }

        setSession(
          getUser(),
          data.access,
          data.refresh || refreshToken
        );

        return data.access;

      } catch (error) {
        clearSession();
        throw error;

      } finally {
        refreshPromise = null;
      }
    })();

    return refreshPromise;
  }

  function isAccessTokenExpired() {
    var token = getToken();

    if (!token) return true;

    try {
      var payload = JSON.parse(
        atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"))
      );

      return payload.exp * 1000 <= Date.now() + 30000;
    } catch (error) {
      return true;
    }
  }

  async function ensureAccessToken() {
    if (!getRefreshToken()) {
      return false;
    }

    if (!getToken() || isAccessTokenExpired()) {
      await refreshSession();
    }

    return Boolean(getToken());
  }

  function getSafeErrorMessage(status, data) {
    if (data && (data.message || data.error || data.detail)) {
      return data.message || data.error || data.detail;
    }

    if (status === 400) return "Los datos proporcionados no son válidos.";
    if (status === 401) return "Correo o contraseña incorrectos.";
    if (status === 403) return "No fue posible completar la operación.";
    if (status === 404) return "No se pudo completar la solicitud.";
    if (status === 429) return "Demasiados intentos. Inténtalo nuevamente más tarde.";
    if (status >= 500) return "El servicio no está disponible temporalmente. Inténtalo nuevamente más tarde.";

    return "Ocurrió un error inesperado. Inténtalo nuevamente.";
  }

  async function request(path, options) {
    options = options || {};

    var headers = Object.assign({}, options.headers || {});
    var requestOptions = Object.assign({}, options);

    var skipRefresh = options.skipRefresh === true;

    delete requestOptions.skipRefresh;

    if (options.json !== undefined) {
      headers["Content-Type"] = "application/json";
      requestOptions.body = JSON.stringify(options.json);
      delete requestOptions.json;
    }

    var token = getToken();

    if (token && !headers.Authorization) {
      headers.Authorization = "Bearer " + token;
    }

    requestOptions.headers = headers;

    var response;

    try {
      response = await fetch(url(path), requestOptions);
    } catch (error) {
      var connectionError = new Error(
        "No se pudo conectar con el servicio. Verifica tu conexión e inténtalo nuevamente."
      );

      connectionError.code = "connection_error";
      throw connectionError;
    }

    if (response.status === 401 && !skipRefresh && getRefreshToken()) {
      try {
        var newToken = await refreshSession();

        headers.Authorization = "Bearer " + newToken;
        requestOptions.headers = headers;

        response = await fetch(url(path), requestOptions);

      } catch (error) {
        clearSession();
        throw error;
      }
    }

    var text = await response.text();
    var data = null;

    if (text) {
      try {
        data = JSON.parse(text);
      } catch (error) {
        data = { raw: text };
      }
    }

    if (!response.ok) {
      var err = new Error(getSafeErrorMessage(response.status, data));
      err.status = response.status;
      err.data = data;
      throw err;
    }

    return data;
  }

  async function logout() {
    var refreshToken = getRefreshToken();

    try {
      if (refreshToken) {
        await request(cfg().endpoints.logout, {
          method: "POST",
          json: {
            refresh: refreshToken
          },
          skipRefresh: true
        });
      }
    } finally {
      clearSession();
    }
  }

  async function registerUser(payload) {
    return request(cfg().endpoints.register, {
      method: "POST",
      json: payload,
      skipRefresh: true
    });
  }

  async function loginUser(email, password) {
    return request(cfg().endpoints.login, {
      method: "POST",
      json: {
        email: email,
        password: password
      },
      skipRefresh: true
    });
  }

  async function refreshAccessToken() {
    return refreshSession();
  }

  async function listFoods() {
    return request(cfg().endpoints.foods, { method: "GET" });
  }

  async function createFood(payload) {
    return request(cfg().endpoints.foods, {
      method: "POST",
      json: payload
    });
  }

  async function listNutritionalProfiles() {
    return request(cfg().endpoints.nutritionalProfiles, {
      method: "GET"
    });
  }

  async function createNutritionalProfile(payload) {
    return request(cfg().endpoints.nutritionalProfiles, {
      method: "POST",
      json: payload
    });
  }

  async function processLlm(prompt) {
    var res = await fetch(
      cfg().AI_BASE + cfg().endpoints.llmProcess,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: "llm", prompt: prompt })
      }
    );

    var data = await res.json().catch(function () {
      return {};
    });

    if (!res.ok) {
      var err = new Error(data.error || data.detail || "Error LLM");
      err.status = res.status;
      err.data = data;
      throw err;
    }

    return data;
  }

  async function analyzeVision(file) {
    var form = new FormData();
    form.append("image", file);

    var res = await fetch(
      cfg().AI_BASE + cfg().endpoints.visionAnalyze,
      {
        method: "POST",
        body: form
      }
    );

    var data = await res.json().catch(function () {
      return {};
    });

    if (!res.ok) {
      var err = new Error(data.error || data.detail || "Error visión");
      err.status = res.status;
      err.data = data;
      throw err;
    }

    return data;
  }

  async function listFoodCategories() {
    return request(cfg().endpoints.foodCategories, {
      method: "GET"
    });
  }

  async function createFoodCategory(payload) {
    return request(cfg().endpoints.foodCategories, {
      method: "POST",
      json: payload
    });
  }

  global.KoraApi = {
    url: url,
    request: request,
    getToken: getToken,
    getRefreshToken: getRefreshToken,
    getUser: getUser,
    setSession: setSession,
    clearSession: clearSession,
    registerUser: registerUser,
    loginUser: loginUser,
    refreshAccessToken: refreshAccessToken,
    refreshSession: refreshSession,
    ensureAccessToken: ensureAccessToken,
    logout: logout,
    listFoods: listFoods,
    createFood: createFood,
    listFoodCategories: listFoodCategories,
    createFoodCategory: createFoodCategory,
    listNutritionalProfiles: listNutritionalProfiles,
    createNutritionalProfile: createNutritionalProfile,
    processLlm: processLlm,
    analyzeVision: analyzeVision
  };

})(window);
