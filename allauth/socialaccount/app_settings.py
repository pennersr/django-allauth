from django.conf import settings

from allauth.account import app_settings as account_settings

# Request e-mail address from 3rd party account provider? E.g. OpenID AX
QUERY_EMAIL = getattr(settings, "SOCIALACCOUNT_QUERY_EMAIL", 
                      account_settings.EMAIL_REQUIRED)

# Attempt to bypass the signup form by using fields (e.g. username,
# email) retrieved from the social account provider. If a conflict
# arises due to a duplicate e-mail signup form will still kick in.
AUTO_SIGNUP = getattr(settings, "SOCIALACCOUNT_AUTO_SIGNUP", True)

# Enable support for django-avatar. When enabled, the profile image of
# the user is copied locally into django-avatar at signup.
AVATAR_SUPPORT = getattr(settings, "SOCIALACCOUNT_AVATAR_SUPPORT",
                         'avatar' in settings.INSTALLED_APPS)


# Provider specific settings
PROVIDERS = getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
