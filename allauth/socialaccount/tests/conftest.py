import time

from django.urls import reverse

import pytest

from allauth.socialaccount.internal import statekit
from allauth.socialaccount.providers.base.constants import AuthProcess
from allauth.tests import MockedResponse, mocked_response


@pytest.fixture
def provider_callback_response():
    def f(client, process=AuthProcess.LOGIN):
        with mocked_response(
            {
                "token_endpoint": "/",
                "userinfo_endpoint": "/",
            },
            MockedResponse(200, "access_token=456", {"content-type": "dummy"}),
            {
                "sub": "sub123",
            },
        ):
            session = client.session
            session[statekit.STATES_SESSION_KEY] = {
                "state456": [{"process": process}, time.time()]
            }
            session.save()

            resp = client.post(
                reverse(
                    "openid_connect_callback",
                    kwargs={"provider_id": "unittest-server"},
                )
                + "?code=123&state=state456"
            )
            return resp

    return f
