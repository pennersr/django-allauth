from datetime import timedelta
from http import HTTPStatus
from unittest.mock import patch

from django.test import Client
from django.utils import timezone

import jwt
import pytest

from allauth.core import context
from allauth.headless.internal.sessionkit import session_store
from allauth.headless.tokens.strategies.jwt.internal import (
    create_access_token,
    create_refresh_token,
)
from allauth.usersessions.internal import usersessionkit
from allauth.usersessions.models import UserSession
from allauth.usersessions.signals import session_client_changed


# viewname, credential, is_resource
ENDPOINTS_TO_TEST = [
    ("headless_rest_framework_jwt_resource", "access-token", True),
    ("headless_ninja:jwt_resource", "access-token", True),
    ("headless_rest_framework_session_resource", "session-token", True),
    ("headless_ninja:session_resource", "session-token", True),
    ("headless:account:current_session", "access-token", False),
    ("headless:account:current_session", "session-token", False),
    ("headless:tokens:refresh", "refresh-token", False),
]
ACCESS_TOKEN_RESOURCE_VIEWNAMES = [
    viewname
    for viewname, credential, is_resource in ENDPOINTS_TO_TEST
    if credential == "access-token" and is_resource
]


@pytest.fixture
def headless_client():
    # "browser" does not require special activity tracking, so these tests are
    # "app" only.
    return "app"


@pytest.fixture(autouse=True)
def activity_settings(settings):
    settings.USERSESSIONS_TRACK_ACTIVITY = True
    settings.HEADLESS_TOKEN_STRATEGY = (
        "allauth.headless.tokens.strategies.jwt.JWTTokenStrategy"
    )
    settings.HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED = True


@pytest.fixture
def tracked_session(auth_client, user):
    return UserSession.objects.create(
        user=user,
        session_key=auth_client.headless_session().session_key,
        ip="127.0.0.1",
        user_agent="old-agent",
        last_seen_at=timezone.now() - timedelta(hours=1),
    )


@pytest.fixture
def jwt_token_pair(tracked_session):
    session = session_store(tracked_session.session_key)
    access = create_access_token(tracked_session.user, session, {})
    refresh = create_refresh_token(tracked_session.user, session)
    session.save()
    return access, refresh


@pytest.fixture
def activity_request(headless_reverse, tracked_session, jwt_token_pair):
    def make_request(viewname, credential, *, is_resource, client=None, **headers):
        client = client if client is not None else Client()
        url = headless_reverse(viewname)
        if credential == "refresh-token":
            return client.post(
                url,
                data={"refresh_token": jwt_token_pair[1]},
                content_type="application/json",
                **headers,
            )
        if credential == "access-token":
            headers["HTTP_AUTHORIZATION"] = f"Bearer {jwt_token_pair[0]}"
        elif credential == "session-token":
            headers["HTTP_X_SESSION_TOKEN"] = tracked_session.session_key
        data = {"userinfo": "1"} if is_resource else None
        return client.get(url, data, **headers)

    return make_request


@pytest.mark.parametrize("viewname,credential,is_resource", ENDPOINTS_TO_TEST)
@pytest.mark.parametrize("track", [False, True])
@pytest.mark.parametrize("stateful", [False, True])
def test_activity(
    activity_request,
    tracked_session,
    settings,
    viewname,
    credential,
    is_resource,
    track,
    stateful,
):
    settings.USERSESSIONS_TRACK_ACTIVITY = track
    settings.HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED = stateful
    old = tracked_session.last_seen_at
    with patch.object(
        usersessionkit,
        "track_activity",
        wraps=usersessionkit.track_activity,
    ) as track_activity:
        response = activity_request(
            viewname,
            credential,
            is_resource=is_resource,
            HTTP_USER_AGENT="new-agent",
            REMOTE_ADDR="192.0.2.1",
        )
    assert track_activity.call_count <= 1
    assert response.status_code == HTTPStatus.OK, response.content
    if is_resource:
        assert response.json()["user_email"] == tracked_session.user.email
    tracked_session.refresh_from_db()
    expected = track and (stateful or credential != "access-token" or not is_resource)
    assert (tracked_session.last_seen_at > old) is expected
    assert tracked_session.ip == ("192.0.2.1" if expected else "127.0.0.1")
    assert tracked_session.user_agent == ("new-agent" if expected else "old-agent")
    assert UserSession.objects.count() == 1


@pytest.mark.parametrize("viewname,credential,is_resource", ENDPOINTS_TO_TEST)
def test_rejected_credentials_do_not_track(
    activity_request, tracked_session, viewname, credential, is_resource
):
    session_store(tracked_session.session_key).delete()
    old = tracked_session.last_seen_at
    response = activity_request(viewname, credential, is_resource=is_resource)
    assert response.status_code in (
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.UNAUTHORIZED,
        HTTPStatus.FORBIDDEN,
        HTTPStatus.GONE,
    ), response.content
    tracked_session.refresh_from_db()
    assert tracked_session.last_seen_at == old
    assert UserSession.objects.count() == 1


@pytest.mark.parametrize("viewname", ACCESS_TOKEN_RESOURCE_VIEWNAMES)
def test_stateless_access_after_session_deleted(
    activity_request, tracked_session, settings, viewname, django_assert_num_queries
):
    settings.HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED = False
    session_store(tracked_session.session_key).delete()
    old = tracked_session.last_seen_at
    with django_assert_num_queries(1):
        response = activity_request(viewname, "access-token", is_resource=True)
    assert response.status_code == HTTPStatus.OK
    tracked_session.refresh_from_db()
    assert tracked_session.last_seen_at == old


@pytest.mark.parametrize("different_user", [False, True])
def test_mixed_credentials_different_sessions(
    activity_request, tracked_session, user_factory, settings, different_user
):
    settings.MIDDLEWARE = [
        *settings.MIDDLEWARE,
        "allauth.usersessions.middleware.UserSessionsMiddleware",
    ]
    token_user_id = tracked_session.user_id
    cookie_user = user_factory() if different_user else tracked_session.user
    cookie_client = Client()
    cookie_client.force_login(cookie_user)
    cookie_key = cookie_client.session.session_key
    old = tracked_session.last_seen_at
    cookie_tracked = UserSession.objects.create(
        user=cookie_user, session_key=cookie_key, ip="127.0.0.1", last_seen_at=old
    )
    response = activity_request(
        "headless_rest_framework_jwt_resource",
        "access-token",
        is_resource=True,
        client=cookie_client,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["user_email"] == tracked_session.user.email
    assert response.wsgi_request.session.session_key == cookie_key
    tracked_session.refresh_from_db()
    cookie_tracked.refresh_from_db()
    assert tracked_session.last_seen_at > old
    assert cookie_tracked.last_seen_at > old
    assert cookie_tracked.user_id == cookie_user.pk
    assert tracked_session.user_id == token_user_id


@pytest.mark.parametrize("viewname", ACCESS_TOKEN_RESOURCE_VIEWNAMES)
def test_expired_access_token_does_not_track(
    jwt_token_pair, tracked_session, settings, headless_reverse, viewname
):
    payload = jwt.decode(jwt_token_pair[0], options={"verify_signature": False})
    payload["exp"] = 0
    expired = jwt.encode(payload, settings.HEADLESS_JWT_PRIVATE_KEY, algorithm="RS256")
    old = tracked_session.last_seen_at
    response = Client().get(
        headless_reverse(viewname), HTTP_AUTHORIZATION=f"Bearer {expired}"
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    tracked_session.refresh_from_db()
    assert tracked_session.last_seen_at == old


@pytest.mark.parametrize("track", [False, True])
def test_headless_login_creates_tracking_record(
    client, user, user_password, headless_reverse, settings, track
):
    settings.USERSESSIONS_TRACK_ACTIVITY = track
    response = client.post(
        headless_reverse("headless:account:login"),
        data={"username": user.username, "password": user_password},
        content_type="application/json",
    )
    assert response.status_code == HTTPStatus.OK, response.content
    assert UserSession.objects.filter(
        session_key=response.json()["meta"]["session_token"]
    ).exists()


@pytest.mark.parametrize("viewname,credential,is_resource", ENDPOINTS_TO_TEST)
def test_activity_signal_receives_original_request(
    activity_request, tracked_session, viewname, credential, is_resource
):
    requests = []

    def on_change(sender, request, to_session, **kwargs):
        assert context.request is request
        assert to_session.user_id == tracked_session.user_id
        assert to_session.session_key == tracked_session.session_key
        requests.append(request)

    session_client_changed.connect(on_change)
    try:
        response = activity_request(
            viewname,
            credential,
            is_resource=is_resource,
            HTTP_USER_AGENT="new-agent",
        )
        assert response.status_code == HTTPStatus.OK
        assert requests == [response.wsgi_request]
    finally:
        session_client_changed.disconnect(on_change)


@pytest.mark.parametrize("viewname", ACCESS_TOKEN_RESOURCE_VIEWNAMES)
@pytest.mark.parametrize(
    "track,stateful,user_agent,queries",
    [
        # Stateful validation: session lookup + token user lookup.
        (False, True, "old-agent", 2),
        # Stateless validation: token user lookup; no session to track.
        (True, False, "old-agent", 1),
        # Stateful validation (2) and a single activity update (1).
        (True, True, "old-agent", 3),
        # A changed user agent adds session and user lookups (2), an
        # update (1), and a savepoint and release (2) after the initial update.
        (True, True, "new-agent", 8),
    ],
)
def test_authentication_query_counts(
    activity_request,
    settings,
    django_assert_num_queries,
    viewname,
    track,
    stateful,
    user_agent,
    queries,
):
    settings.USERSESSIONS_TRACK_ACTIVITY = track
    settings.HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED = stateful
    with django_assert_num_queries(queries):
        response = activity_request(
            viewname, "access-token", is_resource=True, HTTP_USER_AGENT=user_agent
        )
    assert response.status_code == HTTPStatus.OK


def test_stateless_ninja_does_not_resolve_user(
    activity_request, settings, django_assert_num_queries
):
    settings.HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED = False
    with django_assert_num_queries(0):
        response = activity_request(
            "headless_ninja:jwt_resource", "access-token", is_resource=False
        )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("viewname,credential,is_resource", ENDPOINTS_TO_TEST)
def test_usersessions_not_installed(
    activity_request, tracked_session, settings, viewname, credential, is_resource
):
    old = tracked_session.last_seen_at
    settings.INSTALLED_APPS = [
        app for app in settings.INSTALLED_APPS if app != "allauth.usersessions"
    ]
    response = activity_request(viewname, credential, is_resource=is_resource)
    assert response.status_code == HTTPStatus.OK, response.content
    tracked_session.refresh_from_db()
    assert tracked_session.last_seen_at == old


def test_refresh_with_different_access_token_session(
    activity_request, tracked_session, auth_client, settings
):
    settings.MIDDLEWARE = [
        *settings.MIDDLEWARE,
        "allauth.usersessions.middleware.UserSessionsMiddleware",
    ]
    token_client = Client()
    token_client.force_login(tracked_session.user)
    session = token_client.session
    old = tracked_session.last_seen_at
    token_tracked = UserSession.objects.create(
        user=tracked_session.user,
        session_key=session.session_key,
        ip="127.0.0.1",
        last_seen_at=old,
    )
    access = create_access_token(tracked_session.user, session, {})
    cookie_client = Client()
    cookie_client.cookies = auth_client.cookies.copy()
    with patch.object(
        UserSession.objects,
        "create_from_request",
        wraps=UserSession.objects.create_from_request,
    ) as record:
        response = activity_request(
            "headless:tokens:refresh",
            "refresh-token",
            is_resource=False,
            client=cookie_client,
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        assert response.status_code == HTTPStatus.OK
        assert record.call_count == 2
    tracked_session.refresh_from_db()
    token_tracked.refresh_from_db()
    assert tracked_session.last_seen_at > old
    assert token_tracked.last_seen_at > old
