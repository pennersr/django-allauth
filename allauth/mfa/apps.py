from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from allauth import app_settings


class MFAConfig(AppConfig):
    name = "allauth.mfa"
    verbose_name = _("MFA")
    default_auto_field = (
        app_settings.DEFAULT_AUTO_FIELD or "django.db.models.BigAutoField"
    )

    def ready(self):
        from allauth.account import signals as account_signals
        from allauth.mfa import checks  # noqa
        from allauth.mfa import signals

        account_signals._add_email.connect(signals.on_add_email)
