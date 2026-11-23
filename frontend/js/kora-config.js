
(function (global) {
  "use strict";

  var API_BASE =
    global.KORA_API_BASE_URL || "http://localhost:8000";

  var AI_BASE =
    global.KORA_AI_BASE_URL || "http://localhost:8000";

  global.KoraConfig = {
    API_BASE: API_BASE.replace(/\/$/, ""),
    AI_BASE: AI_BASE.replace(/\/$/, ""),

    endpoints: {
      identityHealth: "/api/identity/users/health/",
      register: "/api/identity/users/register/",
      login: "/api/identity/users/login/",
      refresh: "/api/identity/users/token/refresh/",
      logout: "/api/identity/users/logout/",

      businessHealth: "/api/business/health/",
      nutritionalProfiles: "/api/business/nutritional-profiles/",
      foods: "/api/business/foods/",
      foodCategories: "/api/business/food-categories/",

      llmProcess: "/ai/process",
      visionAnalyze: "/vision/analyze"
    },

    storageKeys: {
      user: "kora_user",
      accessToken: "kora_access_token",
      refreshToken: "kora_refresh_token"
    }
  };

  global.KORA_AI_BASE_URL = global.KoraConfig.AI_BASE;
  global.KORA_API_BASE_URL = global.KoraConfig.API_BASE;

})(window);
