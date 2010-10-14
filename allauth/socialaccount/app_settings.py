from django.conf import settings

# Ask user (via signup form) for a username
SIGNUP_USERNAME = getattr(settings, "SOCIALACCOUNT_SIGNUP_USERNAME", False)

# Ask user (via signup form) for an email address. Note: enable
# QUERY_EMAIL to have this field prefilled
SIGNUP_EMAIL = getattr(settings, "SOCIALACCOUNT_SIGNUP_EMAIL", False)

# Request e-mail address from 3rd party account provider? E.g. OpenID AX
QUERY_EMAIL = getattr(settings, "SOCIALACCOUNT_QUERY_EMAIL", True)
