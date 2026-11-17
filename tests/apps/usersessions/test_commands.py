from datetime import timedelta
from importlib import import_module
from unittest.mock import patch

from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.utils import timezone

import pytest

from allauth.usersessions.internal.flows import sessions
from allauth.usersessions.models import UserSession


def create_user_session(user, session_key, **kwargs):
    return UserSession.objects.create(
        user=user,
        ip="127.0.0.1",
        session_key=session_key,
        user_agent="test",
        **kwargs,
    )


@pytest.mark.parametrize(
    "session_engine",
    [
        "django.contrib.sessions.backends.db",
        "django.contrib.sessions.backends.cached_db",
    ],
)
def test_clear_usersessions_db_backend(user, capsys, settings, session_engine):
    settings.SESSION_ENGINE = session_engine
    now = timezone.now()
    Session.objects.bulk_create(
        [
            Session(
                session_key="active",
                session_data="",
                expire_date=now + timedelta(hours=1),
            ),
            Session(
                session_key="expired",
                session_data="",
                expire_date=now - timedelta(hours=1),
            ),
        ]
    )
    active = create_user_session(user, "active")
    create_user_session(user, "expired")
    create_user_session(user, "missing")

    session_store_class = import_module(session_engine).SessionStore
    with patch.object(session_store_class, "load") as load:
        call_command("clear_usersessions", batch_size=1)

    load.assert_not_called()
    assert list(UserSession.objects.values_list("pk", flat=True)) == [active.pk]
    assert "2 expired user session(s) deleted." in capsys.readouterr().out


@override_settings(
    SESSION_ENGINE="django.contrib.sessions.backends.cache",
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "clear-usersessions-tests",
        }
    },
)
def test_clear_usersessions_non_db_backend(user, capsys, settings):
    session_store_class = import_module(
        "django.contrib.sessions.backends.cache"
    ).SessionStore
    store = session_store_class()
    store["test"] = True
    store.save()
    old = timezone.now() - timedelta(seconds=settings.SESSION_COOKIE_AGE + 1)
    active = create_user_session(user, store.session_key, created_at=old)
    create_user_session(user, "missing-1", created_at=old)
    create_user_session(user, "missing-2", created_at=old)
    young = create_user_session(user, "young-missing")

    call_command("clear_usersessions", batch_size=1)

    assert list(UserSession.objects.values_list("pk", flat=True)) == [
        active.pk,
        young.pk,
    ]
    assert "2 expired user session(s) deleted." in capsys.readouterr().out


@override_settings(
    SESSION_ENGINE="django.contrib.sessions.backends.cache",
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "clear-usersessions-error-tests",
        }
    },
)
def test_clear_usersessions_does_not_treat_backend_errors_as_expiry(user, settings):
    old = timezone.now() - timedelta(seconds=settings.SESSION_COOKIE_AGE + 1)
    tracked = create_user_session(user, "session-key", created_at=old)
    session_store_class = import_module(
        "django.contrib.sessions.backends.cache"
    ).SessionStore

    with (
        patch.object(session_store_class, "load", side_effect=RuntimeError),
        pytest.raises(RuntimeError),
    ):
        call_command("clear_usersessions")

    assert UserSession.objects.filter(pk=tracked.pk).exists()


def test_clear_usersessions_avoids_cross_database_subquery(db):
    session_store_class = import_module(
        "django.contrib.sessions.backends.db"
    ).SessionStore

    def db_for_write(model):
        return "sessions" if model is Session else "default"

    with (
        patch(
            "allauth.usersessions.internal.flows.sessions.router.db_for_write",
            side_effect=db_for_write,
        ),
        patch.object(
            sessions,
            "_clear_expired_backend_sessions",
            return_value=0,
        ) as fallback,
    ):
        sessions.clear_expired()

    fallback.assert_called_once_with(
        session_store_class=session_store_class,
        using="default",
        batch_size=sessions.DEFAULT_CLEAR_BATCH_SIZE,
    )


def test_clear_usersessions_rejects_invalid_batch_size(db):
    with pytest.raises(CommandError, match="--batch-size must be greater than zero"):
        call_command("clear_usersessions", batch_size=0)
