#  require django >= 1.7
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SocialaccountConfig(AppConfig):
    name = 'allauth.socialaccount'
    verbose_name = _('Socialaccount')
