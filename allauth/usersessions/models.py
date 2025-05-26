from importlib import import_module
from typing import List

from django.conf import settings
from django.contrib.auth import get_user
from django.core.exceptions import ImproperlyConfigured
from django.db import models, transaction
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from allauth import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.core import context


if not allauth_settings.USERSESSIONS_ENABLED:
    raise ImproperlyConfigured(
        "allauth.usersessions not installed, yet its models are imported."
    )


class UserSessionManager(models.Manager):
    def purge_and_list(self, user) -> List["UserSession"]:
        ret = []
        sessions = UserSession.objects.filter(user=user)
        for session in sessions.iterator():
            if not session.purge():
                ret.append(session)
        return ret

    def create_from_request(self, request: HttpRequest):
        if not request.user.is_authenticated:
            raise ValueError()
        if not request.session.session_key:
            request.session.save()
        ua = request.META.get("HTTP_USER_AGENT", "")[
            0 : UserSession._meta.get_field("user_agent").max_length
        ]

        defaults = dict(
            user=request.user,
            ip=get_adapter().get_client_ip(request),
            user_agent=ua,
        )

        from_session = None
        with transaction.atomic():
            from allauth.usersessions.signals import session_client_changed

            session, created = UserSession.objects.get_or_create(
                session_key=request.session.session_key, defaults=defaults
            )

            if not created:
                from_session = UserSession(
                    session_key=session.session_key,
                    user=session.user,
                    ip=session.ip,
                    user_agent=session.user_agent,
                    data=session.data,
                    created_at=session.created_at,
                    last_seen_at=session.last_seen_at,
                )
                # Update session
                session.user = defaults["user"]
                session.ip = defaults["ip"]
                session.user_agent = defaults["user_agent"]
                session.last_seen_at = timezone.now()

                session.save()

        if from_session and (
            from_session.ip != session.ip
            or from_session.user_agent != session.user_agent
        ):
            session_client_changed.send(
                sender=UserSession,
                request=request,
                from_session=from_session,
                to_session=session,
            )


class UserSession(models.Model):
    objects = UserSessionManager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    ip = models.GenericIPAddressField()
    last_seen_at = models.DateTimeField(default=timezone.now)
    session_key = models.CharField(
        _("session key"), max_length=40, unique=True, editable=False
    )
    user_agent = models.CharField(max_length=200)
    data = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.ip} ({self.user_agent})"

    def _session_store(self, *args):
        engine = import_module(settings.SESSION_ENGINE)
        return engine.SessionStore(*args)

    def exists(self):
        return self._session_store().exists(self.session_key)

    def purge(self):
        purge = not self.exists()
        if not purge:
            # Even if the session still exists, it might be the case that the
            # user session hash is out of sync. So, let's see if
            # `django.contrib.auth` can find a user...
            request = HttpRequest()
            request.session = self._session_store(self.session_key)
            user = get_user(request)
            purge = not user or user.is_anonymous
        if purge:
            self.delete()
            return True
        return False

    def is_current(self):
        return self.session_key == context.request.session.session_key

    def end(self):
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.delete(self.session_key)
        self.delete()
