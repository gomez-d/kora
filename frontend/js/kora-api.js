
(function (global) {
  "use strict";

  function cfg() {
    return global.KoraConfig || {
      API_BASE: "http://localhost:8000",
      endpoints: {},
      storageKeys: { user: "kora_user", token: "kora_token" }
    };
  }

  function url(path) {
    if (!path) return cfg().API_BASE;
    if (/^https?:\/\//i.test(path)) return path;
    return cfg().API_BASE + (path.charAt(0) === "/" ? path : "/" + path);
  }

  function getToken() {
    try {
      return localStorage.getItem(cfg().storageKeys.token) || "";
    } catch (e) {
      return "";
    }
  }

  function getRefreshToken() {
    try {
      return localStorage.getItem(
        cfg().storageKeys.refreshToken
      ) || "";
    } catch (e) {
      return "";
    }
  }

  function getUser() {
    try {
      var raw = localStorage.getItem(cfg().storageKeys.user);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function setSession(user, accessToken, refreshToken) {
    try {
      if (user) localStorage.setItem(cfg().storageKeys.user, JSON.stringify(user));
      if (accessToken) localStorage.setItem(cfg().storageKeys.token, accessToken);
      if (refreshToken) localStorage.setItem(cfg().storageKeys.refreshToken, refreshToken);
    } catch (e) {}
  }

  function clearSession() {
    try {
      localStorage.removeItem(cfg().storageKeys.user);
      localStorage.removeItem(cfg().storageKeys.token);
      localStorage.removeItem(cfg().storageKeys.refreshToken);
    } catch (e) { }
  }

  function getSafeErrorMessage(status) {
    if (status === 400) {
      return "Los datos proporcionados no son válidos.";
    }

    if (status === 401) {
      return "Correo o contraseña incorrectos.";
    }

    if (status === 403) {
      return "No fue posible completar la operación";
    }

    if (status === 404) {
      return "No se pudo completar la solicitud.";
    }

    if (status === 429) {
      return "Demasiados intentos. Inténtalo nuevamente más tarde.";
    }

    if (status >= 500) {
      return "El servicio no está disponible temporalmente. Inténtalo nuevamente más tarde.";
    }

    return "Ocurrió un error inesperado. Inténtalo nuevamente.";
  }

  async function request(path, options) {
    options = options || {};
    
    var retryOnUnauthorized = options.retryOnUnauthorized !== false;

    var requestOptions = Object.assign({}, options);

    delete requestOptions.retryOnUnauthorized;

    var headers = Object.assign({}, requestOptions.headers || {});

    var token = getToken();

    if (token && !headers.Authorization) {
      headers.Authorization = "Bearer " + token;
    }

    if (requestOptions.json !== undefined) {
      headers["Content-Type"] = "application/json";

      requestOptions.body = JSON.stringify(requestOptions.json);

      delete requestOptions.json;
    }

    var res;

    try {
      res = await fetch(url(path), Object.assign({}, requestOptions, {headers: headers}));
    } catch (error) {
      var connectionError = new Error(
        "No se pudo conectar con el servicio. Verifica tu conexión e inténtalo nuevamente."
      );

      connectionError.code = "connection_error";

      throw connectionError;
    }

    var data = null;
    var text = await res.text();

    if (text) {
      try {
        data = JSON.parse(text);
      } catch (e) {
        data = {
          raw: text
        };
      }
    }

    if (res.status === 401 && retryOnUnauthorized && getRefreshToken()) {
      try {
        var newAccessToken = await refreshAccessToken();
        var retryHeaders = Object.assign({}, headers, {Authorization: "Bearer " + newAccessToken});

        return request(path, Object.assign({}, options, {headers: retryHeaders, retryOnUnauthorized: false}));
      } catch (refreshError) {
        clearSession();
        throw refreshError;
      }
    }

    if (!res.ok) {
      var err = new Error(
        getSafeErrorMessage(res.status, data)
      );

      err.status = res.status;
      err.data = data;

      throw err;
    }

    return data;
  }

  async function registerUser(payload) {
  
    return request(cfg().endpoints.register, {
      method: "POST",
      json: payload
    });
  }

  async function loginUser(email, password) {
    return request(cfg().endpoints.login, {
      method: "POST",
      json: {
        email: email,
        password: password
      }
    });
  }

  async function refreshAccessToken() {
    var refreshToken = getRefreshToken();

    if (!refreshToken) {
      throw new Error("No refresh token available.");
    }

    var result = await request(
      cfg().endpoints.refresh,
      {
        method: "POST",
        json: {
          refresh: refreshToken
        },
        retryOnUnauthorized: false
      }
    );

    if (!result || !result.access) {
      throw new Error("Invalid token refresh response.");
    }

    try {
      localStorage.setItem(
        cfg().storageKeys.token,
        result.access
      );
    } catch (e) {}

    return result.access;
  }

  async function listFoods() {
    return request(cfg().endpoints.foods, { method: "GET" });
  }

  async function createFood(payload) {
    return request(cfg().endpoints.foods, { method: "POST", json: payload });
  }

  async function listNutritionalProfiles() {
    return request(cfg().endpoints.nutritionalProfiles, { method: "GET" });
  }

  async function createNutritionalProfile(payload) {
    return request(cfg().endpoints.nutritionalProfiles, {
      method: "POST",
      json: payload
    });
  }

  async function processLlm(prompt) {
    var base = cfg().AI_BASE;
    var res = await fetch(base + cfg().endpoints.llmProcess, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "llm", prompt: prompt })
    });
    var data = await res.json().catch(function () { return {}; });
    if (!res.ok) {
      var err = new Error(data.error || data.detail || "Error LLM");
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  async function analyzeVision(file) {
    var base = cfg().AI_BASE;
    var form = new FormData();
    form.append("image", file);
    var res = await fetch(base + cfg().endpoints.visionAnalyze, {
      method: "POST",
      body: form
    });
    var data = await res.json().catch(function () { return {}; });
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
  async function createFood(payload) {
      return request(cfg().endpoints.foods, {
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

      listFoods: listFoods,
      createFood: createFood,
      createFoodCategory: createFoodCategory,
        listFoodCategories,
      listNutritionalProfiles: listNutritionalProfiles,
      createNutritionalProfile: createNutritionalProfile,
      processLlm: processLlm,
      analyzeVision: analyzeVision
  };

})(window);


