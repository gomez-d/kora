from django.test import TestCase

from users.models import User
from users.serializers import UserRegistrationSerializer

class UserCredentialProtectionTest(TestCase):
    def test_password_is_not_stored_in_plain_text(self):
        raw_password = 'TestPassword123!'

        data = {
            'username': 'test_user',
            'email': 'test@example.com',
            'password': raw_password,
            'first_name': 'Test',
            'last_name': 'User'
        }

        serializer = UserRegistrationSerializer(data = data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertNotEqual(user.password, raw_password)
        self.assertTrue(user.check_password(raw_password))