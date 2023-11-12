from unittest.mock import Mock, patch

from django.urls import reverse

import pytest

from allauth.socialaccount.providers.base.constants import AuthProcess


@pytest.fixture
def provider_callback_response():
    def f(client, process=AuthProcess.LOGIN):
        with patch("requests.get") as get_mock:
            resp = Mock()
            resp.json = Mock()
            resp.json.return_value = {
                "sub": "sub123",
                "token_endpoint": "/",
                "userinfo_endpoint": "/",
            }
            get_mock.return_value = resp
            with patch("requests.post"):
                with patch("requests.request") as request_mock:
                    resp = Mock()
                    resp.status_code = 200
                    resp.headers = {"content-type": "dummy"}
                    resp.text = "access_token=456"
                    request_mock.return_value = resp
                    session = client.session
                    session["socialaccount_state"] = [{"process": process}, None]
                    session.save()

                    resp = client.post(
                        reverse(
                            "openid_connect_callback",
                            kwargs={"provider_id": "unittest-server"},
                        )
                        + "?code=123"
                    )
                    return resp

    return f
