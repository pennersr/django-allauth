from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from allauth import app_settings


class UserSessionsConfig(AppConfig):
    name = "allauth.usersessions"
    verbose_name = _("User Sessions")
    default_auto_field = (
        app_settings.DEFAULT_AUTO_FIELD or "django.db.models.BigAutoField"
    )

    def ready(self):
        from allauth.account.signals import (
            password_changed,
            password_set,
            user_logged_in,
        )
        from allauth.usersessions import signals

        user_logged_in.connect(receiver=signals.on_user_logged_in)
        for sig in [password_set, password_changed]:
            sig.connect(receiver=signals.on_password_changed)
