Configuration
=============

Available settings:

ACCOUNT_ADAPTER (="allauth.account.adapter.DefaultAccountAdapter")
  Specifies the adapter class to use, allowing you to alter certain
  default behaviour.

ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS (=True)
  The default behaviour is to redirect authenticated users to
  ``LOGIN_REDIRECT_URL`` when they try accessing login/signup pages.

  By changing this setting to ``False``, logged in users will not be redirected when
  they access login/signup pages.

ACCOUNT_AUTHENTICATION_METHOD (="username" | "email" | "username_email")
  Specifies the login method to use -- whether the user logs in by
  entering their username, e-mail address, or either one of both.
  Setting this to "email" requires ACCOUNT_EMAIL_REQUIRED=True

ACCOUNT_CONFIRM_EMAIL_ON_GET (=False)
  Determines whether or not an e-mail address is automatically confirmed by
  a GET request. `GET is not designed to modify the server state
  <http://programmers.stackexchange.com/questions/188860/>`_, though it is
  commonly used for email confirmation. To avoid requiring user interaction,
  consider using POST via Javascript in your email confirmation template as
  an alternative to setting this to True.

ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL (=settings.LOGIN_URL)
  The URL to redirect to after a successful e-mail confirmation, in case no
  user is logged in.

ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL (=None)
  The URL to redirect to after a successful e-mail confirmation, in
  case of an authenticated user. Set to ``None`` to use
  ``settings.LOGIN_REDIRECT_URL``.

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS (=3)
  Determines the expiration date of email confirmation mails (# of days).

ACCOUNT_EMAIL_CONFIRMATION_HMAC (=True)
  In order to verify an email address a key is mailed identifying the
  email address to be verified. In previous versions, a record was
  stored in the database for each ongoing email confirmation, keeping
  track of these keys. Current versions use HMAC based keys that do not
  require server side state.

ACCOUNT_EMAIL_REQUIRED (=False)
  The user is required to hand over an e-mail address when signing up.

ACCOUNT_EMAIL_VERIFICATION (="optional")
  Determines the e-mail verification method during signup -- choose
  one of ``"mandatory"``, ``"optional"``, or ``"none"``.
  
  Setting this to `"mandatory"` requires `ACCOUNT_EMAIL_REQUIRED` to be `True`
  
  When set to "mandatory" the user is blocked from logging in until the email
  address is verified. Choose "optional" or "none" to allow logins
  with an unverified e-mail address. In case of "optional", the e-mail
  verification mail is still sent, whereas in case of "none" no e-mail
  verification mails are sent.

ACCOUNT_EMAIL_SUBJECT_PREFIX (="[Site] ")
  Subject-line prefix to use for email messages sent. By default, the
  name of the current ``Site`` (``django.contrib.sites``) is used.

ACCOUNT_DEFAULT_HTTP_PROTOCOL (="http")
  The default protocol used for when generating URLs, e.g. for the
  password forgotten procedure. Note that this is a default only --
  see the section on HTTPS for more information.

ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN (=180)
  The cooldown period (in seconds) after a confirmation email is sent,
  during which further emails are not sent. Note that this cooldown is
  ignored if you are using HMAC confirmation and you need to disable
  HMAC by setting **ACCOUNT_EMAIL_CONFIRMATION_HMAC=False** in order
  for a cooldown to be employed.

ACCOUNT_EMAIL_MAX_LENGTH(=254)
  Maximum length of the email field. You won't need to alter this unless using
  MySQL with the InnoDB storage engine and the ``utf8mb4`` charset, and only in
  versions lower than 5.7.7, because the default InnoDB settings don't allow
  indexes bigger than 767 bytes. When using ``utf8mb4``, characters are 4-bytes
  wide, so at maximum column indexes can be 191 characters long (767/4).
  Unfortunately Django doesn't allow specifying index lengths, so the solution
  is to reduce the length in characters of indexed text fields.
  More information can be found at `MySQL's documentation on converting between
  3-byte and 4-byte Unicode character sets
  <https://dev.mysql.com/doc/refman/5.5/en/charset-unicode-conversion.html>`_.

ACCOUNT_MAX_EMAIL_ADDRESSES(=None)
  The maximum amount of email addresses a user can associate to his account. It
  is safe to change this setting for an already running project -- it will not
  negatively affect users that already exceed the allowed amount. Note that if
  you set the maximum to 1, users will not be able to change their email address
  as they are unable to add the new address, followed by removing the old
  address.


ACCOUNT_FORMS (={})
  Used to override forms, for example:
  ``{'login': 'myapp.forms.LoginForm'}``

  Possible keys (and default values):

  * ``add_email``: :class:`allauth.account.forms.AddEmailForm`
  * ``change_password``: :class:`allauth.account.forms.ChangePasswordForm`
  * ``disconnect``: :class:`allauth.socialaccount.forms.DisconnectForm`
  * ``login``: :class:`allauth.account.forms.LoginForm`
  * ``reset_password``: :class:`allauth.account.forms.ResetPasswordForm`
  * ``reset_password_from_key``: :class:`allauth.account.forms.ResetPasswordKeyForm`
  * ``set_password``: :class:`allauth.account.forms.SetPasswordForm`
  * ``signup``: :class:`allauth.account.forms.SignupForm`
  * ``signup``: :class:`allauth.socialaccount.forms.SignupForm`

ACCOUNT_LOGIN_ATTEMPTS_LIMIT (=5)
  Number of failed login attempts. When this number is
  exceeded, the user is prohibited from logging in for the
  specified ``ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT`` seconds. Set to ``None``
  to disable this functionality. Important: while this protects the
  allauth login view, it does not protect Django's admin login from
  being brute forced.

ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT (=300)
  Time period, in seconds, from last unsuccessful login attempt, during
  which the user is prohibited from trying to log in.

ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION (=False)
  The default behaviour is not log users in and to redirect them to
  ``ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL``.

  By changing this setting to ``True``, users will automatically be logged in once
  they confirm their email address. Note however that this only works when
  confirming the email address **immediately after signing up**, assuming users
  didn't close their browser or used some sort of private browsing mode.

ACCOUNT_LOGOUT_ON_GET (=False)
  Determines whether or not the user is automatically logged out by a
  GET request. `GET is not designed to modify the server state <http://programmers.stackexchange.com/questions/188860/>`_,
  and in this case it can be dangerous. See `LogoutView in the
  documentation <http://django-allauth.readthedocs.io/en/latest/views.html#logout>`_
  for details.

ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE (=False)
  Determines whether or not the user is automatically logged out after
  changing or setting their password. See documentation for
  `Django's session invalidation on password change <https://docs.djangoproject.com/en/stable/topics/auth/default/#session-invalidation-on-password-change>`_.

ACCOUNT_LOGIN_ON_PASSWORD_RESET (=False)
  By changing this setting to ``True``, users will automatically be logged in
  once they have reset their password. By default they are redirected to the
  password reset done page.

ACCOUNT_LOGOUT_REDIRECT_URL (="/")
  The URL (or URL name) to return to after the user logs out. This is
  the counterpart to Django's ``LOGIN_REDIRECT_URL``.

ACCOUNT_PASSWORD_INPUT_RENDER_VALUE (=False)
  ``render_value`` parameter as passed to ``PasswordInput`` fields.

ACCOUNT_PRESERVE_USERNAME_CASING (=True)
  This setting determines whether the username is stored in lowercase
  (``False``) or whether its casing is to be preserved (``True``). Note that when
  casing is preserved, potentially expensive ``__iexact`` lookups are performed
  when filter on username. For now, the default is set to ``True`` to maintain
  backwards compatibility.

ACCOUNT_SESSION_REMEMBER (=None)
  Controls the life time of the session. Set to ``None`` to ask the user
  ("Remember me?"), ``False`` to not remember, and ``True`` to always
  remember.

ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE (=False)
  When signing up, let the user type in their email address twice to avoid
  typo's.

ACCOUNT_SIGNUP_FORM_CLASS (=None)
  A string pointing to a custom form class
  (e.g. 'myapp.forms.SignupForm') that is used during signup to ask
  the user for additional input (e.g. newsletter signup, birth
  date). This class should implement a ``def signup(self, request, user)``
  method, where user represents the newly signed up user.

ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE (=True)
  When signing up, let the user type in their password twice to avoid typos.

ACCOUNT_SIGNUP_REDIRECT_URL (=``settings.LOGIN_REDIRECT_URL``)
  The URL (or URL name) to redirect to directly after signing up. Note that
  users are only redirected to this URL if the signup went through
  uninterruptedly, for example, without any side steps due to email
  verification. If your project requires the user to always pass through certain
  onboarding views after signup, you will have to keep track of state indicating
  whether or not the user successfully onboarded, and handle accordingly.

ACCOUNT_TEMPLATE_EXTENSION (="html")
  A string defining the template extension to use, defaults to ``html``.

ACCOUNT_USERNAME_BLACKLIST (=[])
  A list of usernames that can't be used by user.

ACCOUNT_UNIQUE_EMAIL (=True)
  Enforce uniqueness of e-mail addresses. The ``emailaddress.email``
  model field is set to ``UNIQUE``. Forms prevent a user from registering
  with or adding an additional email address if that email address is
  in use by another account.

ACCOUNT_USER_DISPLAY (=a callable returning ``user.username``)
  A callable (or string of the form ``'some.module.callable_name'``)
  that takes a user as its only argument and returns the display name
  of the user. The default implementation returns ``user.username``.

ACCOUNT_USER_MODEL_EMAIL_FIELD (="email")
  The name of the field containing the ``email``, if any. See custom
  user models.

ACCOUNT_USER_MODEL_USERNAME_FIELD (="username")
  The name of the field containing the ``username``, if any. See custom
  user models.

ACCOUNT_USERNAME_MIN_LENGTH (=1)
  An integer specifying the minimum allowed length of a username.

ACCOUNT_USERNAME_REQUIRED (=True)
  The user is required to enter a username when signing up. Note that
  the user will be asked to do so even if
  ``ACCOUNT_AUTHENTICATION_METHOD`` is set to ``email``. Set to ``False``
  when you do not wish to prompt the user to enter a username.

ACCOUNT_USERNAME_VALIDATORS (=None)
  A path
  (``'some.module.validators.custom_username_validators'``) to a list of
  custom username validators. If left unset, the validators setup
  within the user model username field are used.
  
  Example::
  
      # In validators.py
      
      from django.contrib.auth.validators import ASCIIUsernameValidator

      custom_username_validators = [ASCIIUsernameValidator()]
      
      # In settings.py
      
      ACCOUNT_USERNAME_VALIDATORS = 'some.module.validators.custom_username_validators'

SOCIALACCOUNT_ADAPTER (="allauth.socialaccount.adapter.DefaultSocialAccountAdapter")
  Specifies the adapter class to use, allowing you to alter certain
  default behaviour.

SOCIALACCOUNT_AUTO_SIGNUP (=True)
  Attempt to bypass the signup form by using fields (e.g. username,
  email) retrieved from the social account provider. If a conflict
  arises due to a duplicate e-mail address the signup form will still
  kick in.

SOCIALACCOUNT_EMAIL_VERIFICATION (=ACCOUNT_EMAIL_VERIFICATION)
  As ``ACCOUNT_EMAIL_VERIFICATION``, but for social accounts.

SOCIALACCOUNT_EMAIL_REQUIRED (=ACCOUNT_EMAIL_REQUIRED)
  The user is required to hand over an e-mail address when signing up
  using a social account.

SOCIALACCOUNT_FORMS (={})
  Used to override forms, for example:
  ``{'signup': 'myapp.forms.SignupForm'}``

SOCIALACCOUNT_PROVIDERS (= dict)
  Dictionary containing provider specific settings.

  The 'APP' section for each provider is generic to all providers and
  can also be specified in the database using a ``SocialApp`` model
  instance instead of here. All other sections are provider-specific and
  are documented in the `for each provider separately
  <providers.html>`__.

  Example::

    SOCIALACCOUNT_PROVIDERS = {
        "github": {
            # For each provider, you can choose whether or not the
            # email address(es) retrieved from the provider are to be
            # interpreted as verified.
            "VERIFIED_EMAIL": True
        },
        "google": {
            # For each OAuth based provider, either add a ``SocialApp``
            # (``socialaccount`` app) containing the required client
            # credentials, or list them here:
            "APP": {
                "client_id": "123",
                "secret": "456",
                "key": ""
            },
            # These are provider-specific settings that can only be
            # listed here:
            "SCOPE": [
                "profile",
                "email",
            ],
            "AUTH_PARAMS": {
                "access_type": "online",
            }
        }
    }

SOCIALACCOUNT_QUERY_EMAIL (=ACCOUNT_EMAIL_REQUIRED)
  Request e-mail address from 3rd party account provider? E.g. using
  OpenID AX, or the Facebook "email" permission.

SOCIALACCOUNT_STORE_TOKENS (=True)
  Indicates whether or not the access tokens are stored in the database.
