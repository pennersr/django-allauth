from django.apps import AppConfig

from allauth.compat import ugettext_lazy as _


class AccountConfig(AppConfig):
    name = 'allauth.account'
    verbose_name = _('Accounts')
