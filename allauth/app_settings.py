import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django import template

SOCIALACCOUNT_ENABLED = 'allauth.socialaccount' in settings.INSTALLED_APPS


def check_context_processors():
    allauth_ctx = 'allauth.socialaccount.context_processors.socialaccount'
    ctx_present = False

    if django.VERSION < (1, 8,):
        setting = "settings.TEMPLATE_CONTEXT_PROCESSORS"
        if allauth_ctx in settings.TEMPLATE_CONTEXT_PROCESSORS:
            ctx_present = True
    else:
        for name, engine in template.engines.templates.items():
            if allauth_ctx in engine.get('OPTIONS', {})\
                    .get('context_processors', []):
                ctx_present = True
            else:
                setting = "settings.TEMPLATES['{}']['OPTIONS']['context_processors']"
                setting = setting.format(name)

    if not ctx_present:
        excmsg = ("socialaccount context processor "
                  "not found in {}. "
                  "See settings.py instructions here: "
                  "http://django-allauth.readthedocs.org/en/latest/installation.html")
        raise ImproperlyConfigured(excmsg.format(setting))


if SOCIALACCOUNT_ENABLED:
    check_context_processors()


LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '/')

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
