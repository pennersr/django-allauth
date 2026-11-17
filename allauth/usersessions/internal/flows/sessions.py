from __future__ import annotations

from datetime import timedelta
from importlib import import_module

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.sessions.backends.db import SessionStore as DatabaseSessionStore
from django.db import DEFAULT_DB_ALIAS, router
from django.db.models import Exists, OuterRef
from django.http import HttpRequest
from django.utils import timezone

from allauth.account.internal import flows
from allauth.usersessions.adapter import get_adapter
from allauth.usersessions.models import UserSession


DEFAULT_CLEAR_BATCH_SIZE = 1000


def clear_expired(*, batch_size: int = DEFAULT_CLEAR_BATCH_SIZE) -> int:
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")

    engine = import_module(settings.SESSION_ENGINE)
    session_store_class = engine.SessionStore
    usersession_db = router.db_for_write(UserSession) or DEFAULT_DB_ALIAS

    if issubclass(session_store_class, DatabaseSessionStore):
        session_model = session_store_class.get_model_class()
        session_db = router.db_for_write(session_model) or DEFAULT_DB_ALIAS
        if session_db == usersession_db:
            return _clear_expired_db_sessions(
                session_model=session_model,
                using=usersession_db,
                batch_size=batch_size,
            )

    return _clear_expired_backend_sessions(
        session_store_class=session_store_class,
        using=usersession_db,
        batch_size=batch_size,
    )


def _clear_expired_db_sessions(*, session_model, using: str, batch_size: int) -> int:
    active_sessions = session_model.objects.using(using).filter(
        session_key=OuterRef("session_key"),
        expire_date__gt=timezone.now(),
    )
    expired = UserSession.objects.using(using).filter(~Exists(active_sessions))
    return _delete_in_batches(expired, using=using, batch_size=batch_size)


def _clear_expired_backend_sessions(
    *, session_store_class, using: str, batch_size: int
) -> int:
    deleted = 0
    last_pk = None
    # Currently, there is no way to avoid looping over all sessions. As that is
    # expensive, we'll exclude recent sessions based on SESSION_COOKIE_AGE.
    # Note that this can be stale already -- so downside is that this delays
    # expiry.
    created_before = timezone.now() - timedelta(seconds=settings.SESSION_COOKIE_AGE)
    sessions = (
        UserSession.objects.using(using)
        .filter(created_at__lte=created_before)
        .order_by("pk")
    )
    while True:
        batch = sessions
        if last_pk is not None:
            batch = batch.filter(pk__gt=last_pk)
        rows = list(batch.values_list("pk", "session_key")[:batch_size])
        if not rows:
            break

        expired_pks = []
        for pk, session_key in rows:
            store = session_store_class(session_key=session_key)
            session_data = store.load()
            if not session_data:
                if store.session_key and store.session_key != session_key:
                    store.delete()
                expired_pks.append(pk)
        deleted += _delete_pks(expired_pks, using=using)
        last_pk = rows[-1][0]
    return deleted


def _delete_in_batches(queryset, *, using: str, batch_size: int) -> int:
    deleted = 0
    while True:
        pks = list(queryset.order_by("pk").values_list("pk", flat=True)[:batch_size])
        if not pks:
            break
        deleted += _delete_pks(pks, using=using)
    return deleted


def _delete_pks(pks: list, *, using: str) -> int:
    if not pks:
        return 0
    _, deleted_by_model = UserSession.objects.using(using).filter(pk__in=pks).delete()
    return deleted_by_model.get(UserSession._meta.label, 0)


def end_other_sessions(request: HttpRequest, user: AbstractBaseUser) -> None:
    sessions_to_end = []
    for session in UserSession.objects.filter(user_id=user.pk):
        if session.is_current():
            continue
        sessions_to_end.append(session)
    end_sessions(request, sessions_to_end)


def end_sessions(request: HttpRequest, sessions) -> None:
    has_current = any([session.is_current() for session in sessions])
    get_adapter().end_sessions(sessions)
    if has_current:
        flows.logout.logout(request)
