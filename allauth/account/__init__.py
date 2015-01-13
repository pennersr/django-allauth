# Ok, this is really weird but, in python3.2 we must import app_settings before
# django imports apps; otherwise the module-class hack doesn't work as expected
from django.utils.importlib import import_module


from . import app_settings


def signup_form():
    class_module, form_module, class_name = app_settings.SIGNUP_FORM_CLASS.rsplit('.', 2)
    mod = import_module(form_module)
    return getattr(mod, class_name)()

default_app_config = 'allauth.account.apps.AccountConfig'
