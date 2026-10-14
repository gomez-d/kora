
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

  function getUser() {
    try {
      var raw = localStorage.getItem(cfg().storageKeys.user);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function setSession(user, token) {
    try {
      if (user) localStorage.setItem(cfg().storageKeys.user, JSON.stringify(user));
      if (token) localStorage.setItem(cfg().storageKeys.token, token);
    } catch (e) {}
  }

  function clearSession() {
    try {
      localStorage.removeItem(cfg().storageKeys.user);
      localStorage.removeItem(cfg().storageKeys.token);
    } catch (e) { }
  }

  async function request(path, options) {
    options = options || {};
    var headers = Object.assign({}, options.headers || {});
    var token = getToken();
    if (token && !headers.Authorization) {
      headers.Authorization = "Bearer " + token;
    }
    if (options.json !== undefined) {
      headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(options.json);
      delete options.json;
    }
    var res = await fetch(url(path), Object.assign({}, options, { headers: headers }));
    var data = null;
    var text = await res.text();
    if (text) {
      try {
        data = JSON.parse(text);
      } catch (e) {
        data = { raw: text };
      }
    }
    if (!res.ok) {
      var err = new Error((data && (data.message || data.error || data.detail)) || res.statusText || "Error de red");
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

  async function loginUser(emailOrUsername, password) {
    var loginPath = "/api/identity/users/login/";
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
    listNutritionalProfiles: listNutritionalProfiles,
    createNutritionalProfile: createNutritionalProfile,
    processLlm: processLlm,
    analyzeVision: analyzeVision
  };
})(window);
