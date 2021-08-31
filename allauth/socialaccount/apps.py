from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SocialAccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'    
    name = "allauth.socialaccount"
    verbose_name = _("Social Accounts")
