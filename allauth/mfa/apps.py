from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MFAConfig(AppConfig):
    name = "allauth.mfa"
    verbose_name = _("MFA")
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from allauth.account import signals as account_signals
        from allauth.mfa import signals

        account_signals._add_email.connect(signals.on_add_email)
