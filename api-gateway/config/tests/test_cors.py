from django.test import TestCase


class CorsConfigurationTests(TestCase):
    """
    Verify CORS behavior for allowed and disallowed origins.
    """

    def test_allowed_origin_localhost(self):
        response = self.client.options(
            "/api/health/",
            HTTP_ORIGIN="http://localhost:5500",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            "http://localhost:5500",
        )

    def test_allowed_origin_loopback(self):
        response = self.client.options(
            "/api/health/",
            HTTP_ORIGIN="http://127.0.0.1:5500",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            "http://127.0.0.1:5500",
        )

    def test_disallowed_origin(self):
        response = self.client.options(
            "/api/health/",
            HTTP_ORIGIN="http://localhost:9999",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )

        self.assertIsNone(
            response.headers.get("Access-Control-Allow-Origin")
        )

    def test_preflight_allows_authorization_header(self):
        response = self.client.options(
            "/api/health/",
            HTTP_ORIGIN="http://localhost:5500",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS=(
                "authorization,content-type"
            ),
        )

        self.assertEqual(response.status_code, 200)

        allowed_headers = response.headers.get(
            "Access-Control-Allow-Headers",
            "",
        ).lower()

        self.assertIn("authorization", allowed_headers)
        self.assertIn("content-type", allowed_headers)

    def test_preflight_allows_configured_methods(self):
        response = self.client.options(
            "/api/health/",
            HTTP_ORIGIN="http://localhost:5500",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )

        allowed_methods = response.headers.get(
            "Access-Control-Allow-Methods",
            "",
        )

        for method in [
            "DELETE",
            "GET",
            "OPTIONS",
            "PATCH",
            "POST",
            "PUT",
        ]:
            self.assertIn(method, allowed_methods)