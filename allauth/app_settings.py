from django.conf import settings

SOCIALACCOUNT_ENABLED = 'allauth.socialaccount' in settings.INSTALLED_APPS

if SOCIALACCOUNT_ENABLED:
    assert 'allauth.socialaccount.context_processors.socialaccount' \
        in settings.TEMPLATE_CONTEXT_PROCESSORS

LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '/')

