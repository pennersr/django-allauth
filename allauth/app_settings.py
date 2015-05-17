import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SOCIALACCOUNT_ENABLED = 'allauth.socialaccount' in settings.INSTALLED_APPS


def check_context_processors():
    allauth_ctx = 'allauth.socialaccount.context_processors.socialaccount'
    ctx_present = False

    if django.VERSION < (1, 8,):
        if allauth_ctx in settings.TEMPLATE_CONTEXT_PROCESSORS:
            ctx_present = True
    else:
        for engine in settings.TEMPLATES:
            if allauth_ctx in engine.get('OPTIONS', {})\
                    .get('context_processors', []):
                ctx_present = True
                break

    if not ctx_present:
        excmsg = ("socialaccount context processor "
                  "not found in settings.TEMPLATE_CONTEXT_PROCESSORS."
                  "See settings.py instructions here: "
                  "https://github.com/pennersr/django-allauth#installation")
        raise ImproperlyConfigured(excmsg)


if SOCIALACCOUNT_ENABLED:
    check_context_processors()


LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '/')

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
