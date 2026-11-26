import hashlib

from rest_framework.throttling import SimpleRateThrottle


class PasswordResetRequestIPThrottle(SimpleRateThrottle):
    """
    Limit password recovery requests by client IP address.
    """

    scope = "password_reset_request_ip"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class PasswordResetRequestAccountThrottle(SimpleRateThrottle):
    """
    Limit password recovery requests by email address.
    """

    scope = "password_reset_request_account"

    def get_cache_key(self, request, view):
        email = request.data.get("email")

        if not isinstance(email, str) or not email.strip():
            return None

        normalized_email = email.strip().casefold()

        email_hash = hashlib.sha256(
            normalized_email.encode("utf-8")
        ).hexdigest()

        return self.cache_format % {
            "scope": self.scope,
            "ident": email_hash,
        }


class PasswordResetConfirmIPThrottle(SimpleRateThrottle):
    """
    Limit password reset confirmation attempts by client IP.
    """

    scope = "password_reset_confirm_ip"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }