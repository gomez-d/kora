
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
    return sessionStorage.getItem(
        cfg().storageKeys.accessToken
    ) || "";
}

function getRefreshToken() {
    return sessionStorage.getItem(
        cfg().storageKeys.refreshToken
    ) || "";
}

function getUser() {
    try {
        var raw = sessionStorage.getItem(
            cfg().storageKeys.user
        );

        return raw ? JSON.parse(raw) : null;
    } catch (error) {
        return null;
    }
}

function setSession(user, accessToken, refreshToken) {
    sessionStorage.setItem(
        cfg().storageKeys.user,
        JSON.stringify(user)
    );

    sessionStorage.setItem(
        cfg().storageKeys.accessToken,
        accessToken
    );

    sessionStorage.setItem(
        cfg().storageKeys.refreshToken,
        refreshToken
    );
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
            var response = await fetch(
                url(cfg().endpoints.refresh),
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        refresh: refreshToken
                    })
                }
            );

            var data = await response.json();

            if (!response.ok) {
                throw new Error("No se pudo renovar la sesión.");
            }

            setSession(
                getUser(),
                data.access,
                data.refresh
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

    if (!token) {
        return true;
    }

    try {
        var payload = JSON.parse(
            atob(token.split(".")[1])
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

  async function request(path, options) {

    options = options || {};

    var headers = Object.assign(
        {},
        options.headers || {}
    );

    var requestOptions = Object.assign({}, options);

    delete requestOptions.skipRefresh;

    var skipRefresh = options.skipRefresh === true;

    delete requestOptions.json;

    var token = getToken();

    if (token && !headers.Authorization) {
        headers.Authorization = "Bearer " + token;
    }

    if (options.json !== undefined) {
        headers["Content-Type"] = "application/json";
        requestOptions.body = JSON.stringify(options.json);
    }

    requestOptions.headers = headers;

    var response = await fetch(
        url(path),
        requestOptions
    );

    if (response.status === 401 && !skipRefresh && getRefreshToken()) {

        try {
            var newToken = await refreshSession();

            headers.Authorization = "Bearer " + newToken;

            requestOptions.headers = headers;

            response = await fetch(
                url(path),
                requestOptions
            );

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
        var err = new Error(
            (data && (
                data.message ||
                data.error ||
                data.detail
            )) || "Error de red"
        );

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
            await request(
                cfg().endpoints.logout,
                {
                    method: "POST",
                    json: {
                        refresh: refreshToken
                    },
                    skipRefresh: true
                }
            );
        }

    } finally {
        clearSession();
    }
}

  async function registerUser(payload) {
  
    return request(cfg().endpoints.register, {
      method: "POST",
      json: payload
    });
  }

  async function loginUser(emailOrUsername, password) {
    var loginPath = cfg().endpoints.login;
    try {
      return await request(loginPath, {
        method: "POST",
        json: { username: emailOrUsername, email: emailOrUsername, password: password }
      });
    } catch (e) {
      if (e.status === 404) {
        e.message = "El inicio de sesión aún no está disponible en el backend (falta endpoint de login). Puedes usar el registro.";
      }
      throw e;
    }
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
      getUser: getUser,
      setSession: setSession,
      clearSession: clearSession,
      registerUser: registerUser,
      loginUser: loginUser,

      listFoods: listFoods,
      createFood: createFood,
      createFoodCategory: createFoodCategory,
        listFoodCategories,
      listNutritionalProfiles: listNutritionalProfiles,
      createNutritionalProfile: createNutritionalProfile,
      processLlm: processLlm,
      analyzeVision: analyzeVision,
      getRefreshToken: getRefreshToken,
      refreshSession: refreshSession,
      ensureAccessToken: ensureAccessToken,
      logout: logout,
  };

})(window);


