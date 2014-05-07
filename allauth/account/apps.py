try:
    from django.apps import AppConfig
except ImportError:
    class AppConfig:
        pass

from django.utils.translation import ugettext_lazy as _


class AccountConfig(AppConfig):
    name = 'allauth.account'
    verbose_name = _('Account')
