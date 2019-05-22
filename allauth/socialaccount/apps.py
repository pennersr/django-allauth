from django.apps import AppConfig

from allauth.compat import ugettext_lazy as _


class SocialAccountConfig(AppConfig):
    name = 'allauth.socialaccount'
    verbose_name = _('Social Accounts')
