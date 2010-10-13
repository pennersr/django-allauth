from django.conf import settings

SIGNUP_USERNAME = getattr(settings, "SOCIALACCOUNT_SIGNUP_USERNAME", False)
SIGNUP_EMAIL = getattr(settings, "SOCIALACCOUNT_SIGNUP_EMAIL", False)

