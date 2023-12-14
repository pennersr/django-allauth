from importlib import import_module

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from allauth.account.adapter import get_adapter
from allauth.core import context


class UserSessionManager(models.Manager):
    def purge_and_list(self, user):
        ret = []
        sessions = UserSession.objects.filter(user=user)
        for session in sessions.iterator():
            if not session.purge():
                ret.append(session)
        return ret

    def create_from_request(self, request):
        if not request.user.is_authenticated or not request.session.session_key:
            raise ValueError()
        ua = request.META.get("HTTP_USER_AGENT", "")[
            0 : UserSession._meta.get_field("user_agent").max_length
        ]
        UserSession.objects.update_or_create(
            session_key=request.session.session_key,
            defaults=dict(
                user=request.user,
                ip=get_adapter().get_client_ip(request),
                user_agent=ua,
                last_seen_at=timezone.now(),
            ),
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

    def exists(self):
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        return store.exists(self.session_key)

    def purge(self):
        if not self.exists():
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
