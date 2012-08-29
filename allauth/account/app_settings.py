import warnings
from django.conf import settings

class AuthenticationMethod:
    USERNAME = 'username'
    EMAIL = 'email'
    USERNAME_EMAIL = 'username_email'

# Determines the expiration date of e-mail confirmation mails (# of days)
EMAIL_CONFIRMATION_EXPIRE_DAYS \
    = getattr(settings, "ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS", 
              getattr(settings, "EMAIL_CONFIRMATION_DAYS", 3))

# The URL to redirect to after a successful e-mail confirmation, in case of
# an authenticated user
EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL \
    = getattr(settings, "ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL", settings.LOGIN_REDIRECT_URL)

# The URL to redirect to after a successful e-mail confirmation, in case no
# user is logged in
EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL \
    = getattr(settings, "ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL",
              settings.LOGIN_URL)
                                         
# The user is required to hand over an e-mail address when signing up
EMAIL_REQUIRED = getattr(settings, "ACCOUNT_EMAIL_REQUIRED", False)

# After signing up, keep the user account inactive until the email
# address is verified
EMAIL_VERIFICATION = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION", False)

# Login by email address, not username
if hasattr(settings, "ACCOUNT_EMAIL_AUTHENTICATION"):
    warnings.warn("ACCOUNT_EMAIL_AUTHENTICATION is deprecated, use ACCOUNT_AUTHENTICATION_METHOD", 
                  DeprecationWarning)
    if getattr(settings, "ACCOUNT_EMAIL_AUTHENTICATION"):
        AUTHENTICATION_METHOD = AuthenticationMethod.EMAIL
    else:
        AUTHENTICATION_METHOD = AuthenticationMethod.USERNAME
else:
    AUTHENTICATION_METHOD = getattr(settings, "ACCOUNT_AUTHENTICATION_METHOD", 
                                    AuthenticationMethod.USERNAME)

# Enforce uniqueness of e-mail addresses
UNIQUE_EMAIL = getattr(settings, "ACCOUNT_UNIQUE_EMAIL", True)

# Signup password verification
SIGNUP_PASSWORD_VERIFICATION = getattr(settings, 
                                       "ACCOUNT_SIGNUP_PASSWORD_VERIFICATION", 
                                       True)

# Minimum Password Length
PASSWORD_MIN_LENGTH = getattr(settings, "ACCOUNT_PASSWORD_MIN_LENGTH", 6)

# Subject-line prefix to use for email messages sent
EMAIL_SUBJECT_PREFIX = getattr(settings, "ACCOUNT_EMAIL_SUBJECT_PREFIX", None)

# Signup form
SIGNUP_FORM_CLASS = getattr(settings, "ACCOUNT_SIGNUP_FORM_CLASS", None)

# The user is required to enter a username when signing up
USERNAME_REQUIRED = getattr(settings, "ACCOUNT_USERNAME_REQUIRED", True)

# render_value parameter as passed to PasswordInput fields
PASSWORD_INPUT_RENDER_VALUE = getattr(settings, 
                                      "ACCOUNT_PASSWORD_INPUT_RENDER_VALUE", 
                                      False)

# If login is by email, email must be required
assert (not AUTHENTICATION_METHOD==AuthenticationMethod.EMAIL) or EMAIL_REQUIRED
# If login includes email, login must be unique
assert (AUTHENTICATION_METHOD==AuthenticationMethod.USERNAME) or UNIQUE_EMAIL
assert (not EMAIL_VERIFICATION) or EMAIL_REQUIRED
