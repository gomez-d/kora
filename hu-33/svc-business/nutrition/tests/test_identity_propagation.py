
from uuid import uuid4

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from nutrition.authentication import AuthenticatedIdentity
from nutrition.permissions import HasSelfBusinessPermission


class IdentityPropagationTests(SimpleTestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user_id = uuid4()
        self.other_user_id = uuid4()

        self.identity = AuthenticatedIdentity(
            user_id=str(self.user_id),
            roles=["USER"],
            permissions=["consumptions.read_self"]
        )

        self.permission = HasSelfBusinessPermission()

        self.view = type(
            "TestView",
            (),
            {
                "required_permissions": {
                    "GET": "consumptions.read_self",
                    "POST": "consumptions.read_self"
                }
            }
        )()

    def check_permission(self, request, identity):
        drf_request = Request(request)
        drf_request.user = identity

        return self.permission.has_permission(
            drf_request,
            self.view
        )

    def test_authenticated_user_can_access_without_sending_user_id(self):
        request = self.factory.get("/api/consumptions/")

        self.assertTrue(
            self.check_permission(request, self.identity)
        )

    def test_authenticated_user_cannot_access_another_user(self):
        request = self.factory.get(
            "/api/consumptions/",
            {"user_id": str(self.other_user_id)}
        )

        self.assertFalse(
            self.check_permission(request, self.identity)
        )

    def test_authenticated_user_can_access_own_information(self):
        request = self.factory.get(
            "/api/consumptions/",
            {"user_id": str(self.user_id)}
        )

        self.assertTrue(
            self.check_permission(request, self.identity)
        )

    def test_user_without_required_permission_is_rejected(self):
        identity_without_permission = AuthenticatedIdentity(
            user_id=str(self.user_id),
            roles=["USER"],
            permissions=[]
        )

        request = self.factory.get("/api/consumptions/")

        self.assertFalse(
            self.check_permission(
                request,
                identity_without_permission
            )
        )
