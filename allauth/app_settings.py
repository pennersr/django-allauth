from django.conf import settings

SOCIALACCOUNT_ENABLED = 'allauth.socialaccount' in settings.INSTALLED_APPS

LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '/')

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

USERNAME_AS_HASH = getattr(settings, 'USERNAME_AS_HASH', False)
