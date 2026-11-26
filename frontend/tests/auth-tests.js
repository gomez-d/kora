(function () {
  "use strict";

  var results = document.getElementById("testResults");

  function addResult(name, passed, detail) {
    var item = document.createElement("p");

    item.className = passed
      ? "test-pass"
      : "test-fail";

    item.textContent =
      (passed ? "PASS: " : "FAIL: ") +
      name +
      (detail ? " — " + detail : "");

    results.appendChild(item);
  }

  async function runTest(name, testFunction) {
    try {
      await testFunction();

      addResult(
        name,
        true
      );
    } catch (error) {
      addResult(
        name,
        false,
        error.message
      );
    }
  }

  function assert(condition, message) {
    if (!condition) {
      throw new Error(
        message || "Assertion failed."
      );
    }
  }

  async function runTests() {
    results.innerHTML = "";

    await runTest(
      "KoraApi is available",
      async function () {
        assert(
          window.KoraApi,
          "KoraApi was not loaded."
        );
      }
    );

    await runTest(
        "Successful login returns access and refresh tokens",
        async function () {
            var originalFetch = window.fetch;

            window.fetch = async function () {
                return new Response(
                    JSON.stringify({
                        success: true,
                        message: "Credentials verified successfully.",
                        data: {
                            user_id: "test-user-id",
                            access: "test-access-token",
                            refresh: "test-refresh-token"
                        }
                    }),
                    {
                        status: 200,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            };

            try {
                var result = await KoraApi.loginUser(
                    "test@example.com",
                    "Password123!"
                );

                assert(
                    result.success === true,
                    "Login response was not successful."
                );

                assert(
                    result.data.access === "test-access-token",
                    "Access token was not returned."
                );

                assert(
                    result.data.refresh === "test-refresh-token",
                    "Refresh token was not returned."
                );
            } finally {
                window.fetch = originalFetch;
            }
        }
    );

    await runTest(
        "Invalid credentials return a safe authentication error",
        async function () {
            var originalFetch = window.fetch;

            window.fetch = async function () {
                return new Response(
                    JSON.stringify({
                        detail: "Sensitive authentication detail"
                    }),
                    {
                        status: 401,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            };

            try {
                var errorCaught = null;

                try {
                    await KoraApi.loginUser(
                        "test@example.com",
                        "WrongPassword123!"
                    );
                } catch (error) {
                    errorCaught = error;
                }

                assert(
                    errorCaught,
                    "Expected login to fail."
                );

                assert(
                    errorCaught.status === 401,
                    "Expected status 401."
                );

                assert(
                    errorCaught.message === "Correo o contraseña incorrectos.",
                    "Unexpected authentication error message."
                );

                assert(
                    !errorCaught.message.includes(
                        "Sensitive authentication detail"
                    ),
                    "Sensitive backend detail was exposed."
                );
            } finally {
                window.fetch = originalFetch;
            }
        }
    );

    await runTest(
        "Connection failure returns a safe error message",
        async function () {
            var originalFetch = window.fetch;

            window.fetch = async function () {
                throw new TypeError("Failed to fetch");
            };

            try {
                var errorCaught = null;

                try {
                    await KoraApi.loginUser(
                        "test@example.com",
                        "Password123!"
                    );
                } catch (error) {
                    errorCaught = error;
                }

                assert(
                    errorCaught,
                    "Expected connection failure."
                );

                assert(
                    errorCaught.code === "connection_error",
                    "Expected connection_error code."
                );

                assert(
                    errorCaught.message === "No se pudo conectar con el servicio. Verifica tu conexión e inténtalo nuevamente.",
                    "Unexpected connection error message."
                );

                assert(
                    !errorCaught.message.includes("Failed to fetch"),
                    "Technical network detail was exposed."
                );
            } finally {
                window.fetch = originalFetch;
            }
        }
    );

    await runTest(
        "Successful registration returns user data",
        async function () {
            var originalFetch = window.fetch;

            window.fetch = async function () {
                return new Response(
                    JSON.stringify({
                        success: true,
                        message: "User registered successfully.",
                        data: {
                            user_id: "registered-user-id",
                            email: "newuser@example.com",
                            first_name: "Test",
                            last_name: "User"
                        }
                    }),
                    {
                        status: 201,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            };

            try {
                var result = await KoraApi.registerUser({
                    email: "newuser@example.com",
                    password: "Password123!",
                    first_name: "Test",
                    last_name: "User",
                    date_of_birth: "2000-05-20"
                });

                assert(
                    result.success === true,
                    "Registration response was not successful."
                );

                assert(
                    result.data.user_id === "registered-user-id",
                    "Registered user ID was not returned."
                );

                assert(
                    result.data.email === "newuser@example.com",
                    "Registered email was not returned."
                );
            } finally {
                window.fetch = originalFetch;
            }
        }
    );

    await runTest(
        "Invalid registration data returns a safe validation error",
        async function () {
            var originalFetch = window.fetch;

            window.fetch = async function () {
                return new Response(
                    JSON.stringify({
                        errors: {
                            email: [
                                "Sensitive internal validation detail"
                            ]
                        }
                    }),
                    {
                        status: 400,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            };

            try {
                var errorCaught = null;

                try {
                    await KoraApi.registerUser({
                        email: "invalid",
                        password: "Password123!",
                        first_name: "Test",
                        last_name: "User",
                        date_of_birth: "2000-05-20"
                    });
                } catch (error) {
                    errorCaught = error;
                }

                assert(
                    errorCaught,
                    "Expected registration to fail."
                );

                assert(
                    errorCaught.status === 400,
                    "Expected status 400."
                );

                assert(
                    errorCaught.message === "Los datos proporcionados no son válidos.",
                    "Unexpected registration error message."
                );

                assert(
                    !errorCaught.message.includes(
                        "Sensitive internal validation detail"
                    ),
                    "Sensitive backend validation detail was exposed."
                );
            } finally {
                window.fetch = originalFetch;
            }
        }
    );

    await runTest(
        "Too many attempts return a safe error message",
        async function () {
            var originalFetch = window.fetch;

            window.fetch = async function () {
                return new Response(
                    JSON.stringify({
                        detail: "Internal throttle configuration"
                    }),
                    {
                        status: 429,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            };

            try {
                var errorCaught = null;

                try {
                    await KoraApi.loginUser(
                        "test@example.com",
                        "Password123!"
                    );
                } catch (error) {
                    errorCaught = error;
                }

                assert(
                    errorCaught,
                    "Expected request to fail."
                );

                assert(
                    errorCaught.status === 429,
                    "Expected status 429."
                );

                assert(
                    errorCaught.message === "Demasiados intentos. Inténtalo nuevamente más tarde.",
                    "Unexpected rate limit error message."
                );
            } finally {
                window.fetch = originalFetch;
            }
        }
    );

    await runTest(
        "Server failure returns a safe error message",
        async function () {
            var originalFetch = window.fetch;

            window.fetch = async function () {
                return new Response(
                    JSON.stringify({
                        detail: "Internal server exception"
                    }),
                    {
                        status: 500,
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );
            };

            try {
                var errorCaught = null;

                try {
                    await KoraApi.loginUser(
                        "test@example.com",
                        "Password123!"
                    );
                } catch (error) {
                    errorCaught = error;
                }

                assert(
                    errorCaught,
                    "Expected request to fail."
                );

                assert(
                    errorCaught.status === 500,
                    "Expected status 500."
                );

                assert(
                    errorCaught.message === "El servicio no está disponible temporalmente. Inténtalo nuevamente más tarde.",
                    "Unexpected server error message."
                );
            } finally {
                window.fetch = originalFetch;
            }
        }
    );

    await runTest(
        "Session storage saves user, access and refresh tokens",
        async function () {
            KoraApi.clearSession();

            KoraApi.setSession(
                { user_id: "test-user-id" },
                "test-access-token",
                "test-refresh-token"
            );

            var user = KoraApi.getUser();
            var accessToken = KoraApi.getToken();
            var refreshToken = KoraApi.getRefreshToken();

            assert(
                user && user.user_id === "test-user-id",
                "User data was not stored correctly."
            );

            assert(
                accessToken === "test-access-token",
                "Access token was not stored correctly."
            );

            assert(
                refreshToken === "test-refresh-token",
                "Refresh token was not stored correctly."
            );

            KoraApi.clearSession();
        }
    );

    await runTest(
        "Session storage saves user, access and refresh tokens",
        async function () {
            KoraApi.clearSession();

            KoraApi.setSession(
                { user_id: "test-user-id" },
                "test-access-token",
                "test-refresh-token"
            );

            var user = KoraApi.getUser();
            var accessToken = KoraApi.getToken();
            var refreshToken = KoraApi.getRefreshToken();

            assert(
                user && user.user_id === "test-user-id",
                "User data was not stored correctly."
            );

            assert(
                accessToken === "test-access-token",
                "Access token was not stored correctly."
            );

            assert(
                refreshToken === "test-refresh-token",
                "Refresh token was not stored correctly."
            );

            KoraApi.clearSession();
        }
    );
  }

  runTests();
})();