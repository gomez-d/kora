
(function (global) {
  "use strict";

  var origin = global.location && global.location.origin
    ? global.location.origin
    : "";

var isDockerFrontend =
    global.location &&
    (global.location.port === "5500" ||
    global.location.port === "8080" ||
    global.location.port === "80" ||
    global.location.port === "");


  var API_BASE =
    global.KORA_API_BASE_URL ||
    (isDockerFrontend ? origin : "http://localhost:8000");

  var AI_BASE =
      global.KORA_AI_BASE_URL ||
      (isDockerFrontend ? origin : "http://localhost:8000");

  global.KoraConfig = {
    API_BASE: API_BASE.replace(/\/$/, ""),
    AI_BASE: AI_BASE.replace(/\/$/, ""),

endpoints: {
    identityHealth: "/api/identity/users/health/",
    register: "/api/identity/users/register/",

    businessHealth: "/api/business/health/",
    nutritionalProfiles: "/api/business/nutritional-profiles/",

    foods: "/api/business/foods/",
    foodCategories: "/api/business/food-categories/",

    // AI endpoints
    llmProcess: "/ai/process",
    visionAnalyze: "/vision/analyze"
},


    storageKeys: {
      user: "kora_user",
      token: "kora_token"
    }
  };

  // Compatibilidad con scripts existentes
  global.KORA_AI_BASE_URL = global.KoraConfig.AI_BASE;
  global.KORA_API_BASE_URL = global.KoraConfig.API_BASE;
})(window);
