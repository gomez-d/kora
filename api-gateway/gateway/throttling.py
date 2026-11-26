from rest_framework.throttling import SimpleRateThrottle


class IPRateThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        ident = request.META.get("REMOTE_ADDR")

        if not ident:
            return None

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident
        }


class LoginRateThrottle(IPRateThrottle):
    scope = "login"


class RegistrationRateThrottle(IPRateThrottle):
    scope = "registration"


class RefreshRateThrottle(IPRateThrottle):
    scope = "refresh"

class PasswordResetRequestRateThrottle(IPRateThrottle):
    """
    Limit password recovery requests by client IP.
    """
    scope = "password_reset_request"

class PasswordResetConfirmRateThrottle(IPRateThrottle):
    """
    Limit password reset confirmation requests by client IP.
    """
    scope = "password_reset_confirm"

class AuthenticatedUserRateThrottle(SimpleRateThrottle):
    scope = "authenticated_user"

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None

        user_id = request.user.id

        if not user_id:
            return None

        return self.cache_format % {
            "scope": self.scope,
            "ident": user_id
        }
