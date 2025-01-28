from allauth.headless.constants import Client
from allauth.headless.contrib.rest_framework.authentication import (
    XSessionTokenAuthentication,
)


def test_authenticate(rf, user, headless_client, auth_client):
    if headless_client == Client.BROWSER:
        return
    request = rf.get("/", HTTP_X_SESSION_TOKEN=auth_client.session_token)
    auth_user, session = XSessionTokenAuthentication().authenticate(request)
    assert auth_user.pk == user.pk


def test_invalid_authentication(rf, user, headless_client, auth_client):
    if headless_client == Client.BROWSER:
        return
    request = rf.get("/", HTTP_X_SESSION_TOKEN="wrong")
    result = XSessionTokenAuthentication().authenticate(request)
    assert result is None
