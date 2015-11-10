# Ok, this is really weird but, in python3.2 we must import
# app_settings before django imports apps; otherwise the module-class
# hack doesn't work as expected
from . import app_settings  # noqa

default_app_config = 'allauth.account.apps.AccountConfig'
