from django.conf import settings

## COnfiguration options for Account Authentication
USERNAME = "username"
EMAIL = "email"
BOTH = "username_email"

# The user is required to hand over an e-mail address when signing up
EMAIL_REQUIRED = getattr(settings, "ACCOUNT_EMAIL_REQUIRED", False)

# After signing up, keep the user account inactive until the email
# address is verified
EMAIL_VERIFICATION = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION", False)

# Login by email address, username or both Default is by username
ACCOUNT_AUTHENTICATION = getattr(settings, "ACCOUNT_AUTHENTICATION", USERNAME)

# Enforce uniqueness of e-mail addresses
UNIQUE_EMAIL = getattr(settings, "ACCOUNT_UNIQUE_EMAIL", True)

# Signup password verification
SIGNUP_PASSWORD_VERIFICATION = getattr(settings, "ACCOUNT_SIGNUP_PASSWORD_VERIFICATION", True)

# Subject-line prefix to use for email messages sent
EMAIL_SUBJECT_PREFIX = getattr(settings, "ACCOUNT_EMAIL_SUBJECT_PREFIX", None)

# Signup form
SIGNUP_FORM_CLASS = getattr(settings, "ACCOUNT_SIGNUP_FORM_CLASS", None)

# The user is required to enter a username when signing up
USERNAME_REQUIRED = getattr(settings, "ACCOUNT_USERNAME_REQUIRED", True)

# render_value parameter as passed to PasswordInput fields
PASSWORD_INPUT_RENDER_VALUE = getattr(settings, "ACCOUNT_PASSWORD_INPUT_RENDER_VALUE", False)

assert (ACCOUNT_AUTHENTICATION == USERNAME) or EMAIL_REQUIRED
assert (ACCOUNT_AUTHENTICATION == USERNAME) or UNIQUE_EMAIL
assert (not EMAIL_VERIFICATION) or EMAIL_REQUIRED

