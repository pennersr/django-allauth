import time

import pytest

from allauth.account.authentication import AUTHENTICATION_METHODS_SESSION_KEY
from allauth.account.internal.flows.reauthentication import did_recently_reauthenticate


@pytest.mark.parametrize("reauthenticated", [False, True])
def test_did_recently_reauthenticate(user, request_factory, reauthenticated):
    request = request_factory.get("/")
    request.user = user
    request.session[AUTHENTICATION_METHODS_SESSION_KEY] = [
        {
            "method": "password",
            "at": time.time(),
            "reauthenticated": reauthenticated,
        }
    ]

    assert did_recently_reauthenticate(request) is reauthenticated
