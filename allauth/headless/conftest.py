from django.test.client import Client
from django.urls import reverse

import pytest


@pytest.fixture(params=["app", "browser"])
def headless_client(request):
    return request.param


@pytest.fixture
def headless_reverse(headless_client):
    def rev(viewname, **kwargs):
        viewname = viewname.replace("headless:", f"headless:{headless_client}:")
        return reverse(viewname, **kwargs)

    return rev


class AppClient(Client):
    session_token = None

    def generic(self, *args, **kwargs):
        if self.session_token:
            kwargs["HTTP_X_SESSION_TOKEN"] = self.session_token
        resp = super().generic(*args, **kwargs)
        if resp["content-type"] == "application/json":
            data = resp.json()
            session_token = data.get("meta", {}).get("session_token")
            if session_token:
                self.session_token = session_token
        return resp

    def force_login(self, user):
        ret = super().force_login(user)
        self.session_token = self.session.session_key
        return ret


@pytest.fixture
def app_client():
    return AppClient()


@pytest.fixture
def client(headless_client):
    if headless_client == "browser":
        return Client()
    return AppClient()


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client
