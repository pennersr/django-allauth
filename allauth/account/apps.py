from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


class AccountConfig(AppConfig):
    name = "allauth.account"
    verbose_name = _("Accounts")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        required_mw = "allauth.account.middleware.AccountMiddleware"
        if required_mw not in settings.MIDDLEWARE:
            raise ImproperlyConfigured(
                f"{required_mw} must be added to settings.MIDDLEWARE"
            )
