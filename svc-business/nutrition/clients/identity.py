import requests
from django.conf import settings


def user_exists(user_id):
    url = (
        f"{settings.IDENTITY_SERVICE_URL}"
        f"/api/users/users/{user_id}"
    )

    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException:
        return None

    if response.status_code == 200:
        return True

    if response.status_code == 404:
        return False

    return None
