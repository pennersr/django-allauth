from unittest.mock import Mock

from django.contrib.auth.models import AnonymousUser

import pytest

from allauth.usersessions.middleware import UserSessionsMiddleware
from allauth.usersessions.models import UserSession


def test_mw_without_request_user(rf, db, settings):
    settings.USERSESSIONS_TRACK_ACTIVITY = True
    mw = UserSessionsMiddleware(lambda request: None)
    request = rf.get("/")
    mw(request)
    assert UserSession.objects.count() == 0


@pytest.mark.parametrize("track_activity", [False, True])
def test_mw_with_request_user(rf, db, settings, user, track_activity):
    settings.USERSESSIONS_TRACK_ACTIVITY = track_activity
    mw = UserSessionsMiddleware(lambda request: None)
    request = rf.get("/")
    request.user = user
    request.session = Mock()
    request.session.session_key = "sess-123"
    mw(request)
    assert (
        UserSession.objects.filter(session_key="sess-123", user=user).exists()
        is track_activity
    )


def test_mw_with_anonymous_request_user(rf, db, settings):
    settings.USERSESSIONS_TRACK_ACTIVITY = True
    mw = UserSessionsMiddleware(lambda request: None)
    request = rf.get("/")
    request.user = AnonymousUser()
    request.session = Mock()
    request.session.session_key = "sess-123"
    mw(request)
    assert not UserSession.objects.exists()
