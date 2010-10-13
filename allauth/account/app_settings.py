from django.conf import settings

EMAIL_REQUIRED = getattr(settings, "ACCOUNT_EMAIL_REQUIRED", False)
EMAIL_VERIFICATION = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION", False)
EMAIL_AUTHENTICATION = getattr(settings, "ACCOUNT_EMAIL_AUTHENTICATION", False)
UNIQUE_EMAIL = getattr(settings, "ACCOUNT_UNIQUE_EMAIL", False)
