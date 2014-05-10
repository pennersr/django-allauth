#  require django >= 1.7
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AccountConfig(AppConfig):
    name = 'allauth.account'
    verbose_name = _('Accounts')
