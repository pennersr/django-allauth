from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MFAConfig(AppConfig):
    name = "allauth.mfa"
    verbose_name = _("MFA")
    default_auto_field = "django.db.models.BigAutoField"
