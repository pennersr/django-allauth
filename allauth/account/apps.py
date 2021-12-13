from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountConfig(AppConfig):
    name = "allauth.account"
    verbose_name = _("Accounts")
    default_auto_field = "django.db.models.AutoField"
