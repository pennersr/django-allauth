from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from allauth import app_settings


class SocialAccountConfig(AppConfig):
    name = "allauth.socialaccount"
    verbose_name = _("Social Accounts")
    default_auto_field = app_settings.DEFAULT_AUTO_FIELD or "django.db.models.AutoField"

    def ready(self):
        from allauth.socialaccount.providers import registry

        registry.load()
