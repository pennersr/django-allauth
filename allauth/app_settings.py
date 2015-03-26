import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SOCIALACCOUNT_ENABLED = 'allauth.socialaccount' in settings.INSTALLED_APPS

if SOCIALACCOUNT_ENABLED:
    allauth_ctx = 'allauth.socialaccount.context_processors.socialaccount'
    ctx_present = True

    if django.VERSION < (1, 8,):
        if allauth_ctx not in settings.TEMPLATE_CONTEXT_PROCESSORS:
            ctx_present = False
    else:
        for engine in settings.TEMPLATES:
            if allauth_ctx not in engine.get('OPTIONS', {})\
                    .get('context_processors', []):
                ctx_present = False
                break

    if not ctx_present:
        raise ImproperlyConfigured("socialaccount context processor "
                    "not found in settings.TEMPLATE_CONTEXT_PROCESSORS."
                    "See settings.py instructions here: "
                    "https://github.com/pennersr/django-allauth#installation")


LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '/')

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
