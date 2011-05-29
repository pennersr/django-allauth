from django.conf import settings

# The user is required to hand over an e-mail address when signing up
EMAIL_REQUIRED = getattr(settings, "ACCOUNT_EMAIL_REQUIRED", False)

# After signing up, keep the user account inactive until the email
# address is verified
EMAIL_VERIFICATION = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION", False)

# Login by email address, not username
EMAIL_AUTHENTICATION = getattr(settings, "ACCOUNT_EMAIL_AUTHENTICATION", False)

# Enforce uniqueness of e-mail addresses
UNIQUE_EMAIL = getattr(settings, "ACCOUNT_UNIQUE_EMAIL", True)

# Signup password verification
SIGNUP_PASSWORD_VERIFICATION = getattr(settings, "ACCOUNT_SIGNUP_PASSWORD_VERIFICATION", True)

# The user is required to enter a username when signing up
USERNAME_REQUIRED = getattr(settings, "ACCOUNT_USERNAME_REQUIRED", True)

assert (not EMAIL_AUTHENTICATION) or EMAIL_REQUIRED
assert (not EMAIL_AUTHENTICATION) or UNIQUE_EMAIL
assert (not EMAIL_VERIFICATION) or EMAIL_REQUIRED



