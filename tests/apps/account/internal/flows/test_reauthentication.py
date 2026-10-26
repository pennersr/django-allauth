import time

import pytest

from allauth.account.internal.flows.login import record_authentication
from allauth.account.internal.flows.reauthentication import did_recently_reauthenticate


@pytest.mark.parametrize("reauthenticated", [False, True])
def test_did_recently_reauthenticate(user, request_factory, reauthenticated):
    request = request_factory.get("/")
    request.user = user
    record_authentication(
        request,
        user,
        method="password",
        at=time.time(),
        reauthenticated=reauthenticated,
    )

    assert did_recently_reauthenticate(request) is reauthenticated


def test_reauthentication_record_is_bound_to_user(user, user_factory, request_factory):
    other_user = user_factory()
    request = request_factory.get("/")
    request.user = user
    record_authentication(
        request,
        other_user,
        method="password",
        reauthenticated=True,
    )

    assert not did_recently_reauthenticate(request)
