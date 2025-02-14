Configuration
=============

Available settings:

``ACCOUNT_ADAPTER`` (default: ``"allauth.account.adapter.DefaultAccountAdapter"``)
  Specifies the adapter class to use, allowing you to alter certain
  default behaviour.

``ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS`` (default: ``True``)
  The default behaviour is to redirect authenticated users to
  ``LOGIN_REDIRECT_URL`` when they try accessing login/signup pages.

  By changing this setting to ``False``, logged in users will not be redirected when
  they access login/signup pages.

``ACCOUNT_CHANGE_EMAIL`` (default: ``False``)
  When disabled (``False``), users can add one or more email addresses (up to a
  maximum of ``ACCOUNT_MAX_EMAIL_ADDRESSES``) to their account and freely manage
  those email addresses. When enabled (``True``), users are limited to having
  exactly one email address that they can change by adding a temporary second
  email address that, when verified, replaces the current email address.

``ACCOUNT_CONFIRM_EMAIL_ON_GET`` (default: ``False``)
  Determines whether or not an email address is automatically confirmed by
  a GET request. `GET is not designed to modify the server state
  <http://programmers.stackexchange.com/questions/188860/>`_, though it is
  commonly used for email confirmation. To avoid requiring user interaction,
  consider using POST via Javascript in your email confirmation template as
  an alternative to setting this to True.

``ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL`` (default: ``settings.LOGIN_URL``)
  The URL to redirect to after a successful email confirmation, in case no
  user is logged in.

``ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL`` (default: ``None``)
  The URL to redirect to after a successful email confirmation, in
  case of an authenticated user. Set to ``None`` to use
  ``settings.LOGIN_REDIRECT_URL``.

``ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS`` (default: ``3``)
  Determines the expiration date of email confirmation mails (# of days).

``ACCOUNT_EMAIL_CONFIRMATION_HMAC`` (default: ``True``)
  In order to verify an email address a key is mailed identifying the
  email address to be verified. In previous versions, a record was
  stored in the database for each ongoing email confirmation, keeping
  track of these keys. Current versions use HMAC based keys that do not
  require server side state.

``ACCOUNT_EMAIL_NOTIFICATIONS`` (default: ``False``)
  When enabled, account related security notifications, such as "Your password
  was changed", including information on user agent / IP address from where the
  change originated, will be emailed.

``ACCOUNT_EMAIL_VERIFICATION`` (default: ``"optional"``)
  Determines the email verification method during signup -- choose
  one of ``"mandatory"``, ``"optional"``, or ``"none"``.

  Setting this to ``"mandatory"`` requires ``ACCOUNT_EMAIL_REQUIRED`` to be ``True``.

  When set to ``"mandatory"`` the user is blocked from logging in until the email
  address is verified. Choose ``"optional"`` or ``"none"`` to allow logins
  with an unverified email address. In case of ``"optional"``, the email
  verification mail is still sent, whereas in case of "none" no email
  verification mails are sent.

``ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED`` (default: ``False``)
  Controls whether email verification is performed by means of following a link
  in the email (``False``), or by entering a code (``True``).

``ACCOUNT_EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS`` (default: ``3``)
  This setting controls the maximum number of attempts the user has at inputting
  a valid code.

``ACCOUNT_EMAIL_VERIFICATION_BY_CODE_TIMEOUT`` (default: ``900``)
  The code that is emailed has a limited life span. It expires this many seconds after
  which it was sent.

``ACCOUNT_EMAIL_SUBJECT_PREFIX`` (default: ``"[Site] "``)
  Subject-line prefix to use for email messages sent. By default, the
  name of the current ``Site`` (``django.contrib.sites``) is used.

``ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS`` (default: ``True``)
  Configures whether password reset attempts for email addresses which do not
  have an account result in sending an email.

``ACCOUNT_DEFAULT_HTTP_PROTOCOL`` (default: ``"http"``)
  The default protocol used for when generating URLs, e.g. for the
  password forgotten procedure. Note that this is a default only --
  see the section on HTTPS for more information.

``ACCOUNT_EMAIL_MAX_LENGTH`` (default: ``254``)
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

``ACCOUNT_MAX_EMAIL_ADDRESSES`` (default: ``None``)
  The maximum amount of email addresses a user can associate to his account. It
  is safe to change this setting for an already running project -- it will not
  negatively affect users that already exceed the allowed amount. Note that if
  you set the maximum to 1, users will not be able to change their email
  address.


``ACCOUNT_FORMS``
  Used to override the builtin forms. Defaults to::

    ACCOUNT_FORMS = {
        'add_email': 'allauth.account.forms.AddEmailForm',
        'change_password': 'allauth.account.forms.ChangePasswordForm',
        'confirm_login_code': 'allauth.account.forms.ConfirmLoginCodeForm',
        'login': 'allauth.account.forms.LoginForm',
        'request_login_code': 'allauth.account.forms.RequestLoginCodeForm',
        'reset_password': 'allauth.account.forms.ResetPasswordForm',
        'reset_password_from_key': 'allauth.account.forms.ResetPasswordKeyForm',
        'set_password': 'allauth.account.forms.SetPasswordForm',
        'signup': 'allauth.account.forms.SignupForm',
        'user_token': 'allauth.account.forms.UserTokenForm',
    }

``ACCOUNT_LOGIN_BY_CODE_ENABLED`` (default: ``False``)
  "Login by email" offers an alternative method of logging in. Instead of
  entering an email address and accompanying password, the user only enters the
  email address.  Then, a one-time code is sent to that email address which
  allows the user to login. This method is often referred to as "Magic Code
  Login".  This setting controls whether or not this method of logging in is
  enabled.

``ACCOUNT_LOGIN_BY_CODE_MAX_ATTEMPTS`` (default: ``3``)
  This setting controls the maximum number of attempts the user has at inputting
  a valid code.

``ACCOUNT_LOGIN_BY_CODE_REQUIRED`` (default: ``False``)
  When enabled (in case of ``True``), every user logging in is required to input
  a login confirmation code sent by email.  Alternatively, you can specify a set
  of authentication methods (``"password"``, ``"mfa"``, or ``"socialaccount"``)
  for which login codes are required.

``ACCOUNT_LOGIN_BY_CODE_TIMEOUT`` (default: ``180``)
  The code that is emailed has a limited life span. It expires this many seconds after
  which it was sent.

``ACCOUNT_LOGIN_METHODS`` (default: ``{"username"}``, options: ``"email"`` or ``"username"``)
  Specifies the login method to use -- whether the user logs in by entering
  their username, email address, or either one of both.  Setting this to include
  ``"email"`` requires ``ACCOUNT_EMAIL_REQUIRED=True``

``ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION`` (default: ``False``)
  The default behavior is not log users in and to redirect them to
  ``ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL``.

  By changing this setting to ``True``, users will automatically be logged in once
  they confirm their email address. Note however that this only works when
  confirming the email address **immediately after signing up**, assuming users
  didn't close their browser or used some sort of private browsing mode.

  Note that this setting only affects email verification by link. It has no affect in
  case you turn on code based verification
  (``ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED``).

``ACCOUNT_LOGIN_ON_PASSWORD_RESET`` (default: ``False``)
  By changing this setting to ``True``, users will automatically be logged in
  once they have reset their password. By default they are redirected to the
  password reset done page.

``ACCOUNT_LOGIN_TIMEOUT`` (default: ``900``)
  The maximum allowed time (in seconds) for a login to go through the
  various login stages. This limits, for example, the time span that the
  2FA stage remains available.

``ACCOUNT_LOGOUT_ON_GET`` (default: ``False``)
  Determines whether or not the user is automatically logged out by a
  GET request. `GET is not designed to modify the server state <http://programmers.stackexchange.com/questions/188860/>`_,
  and in this case it can be dangerous. See `LogoutView in the
  documentation <https://docs.allauth.org/en/latest/account/views.html#logout>`_
  for details.

``ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE`` (default: ``False``)
  Determines whether or not the user is automatically logged out after
  changing or setting their password. See documentation for
  `Django's session invalidation on password change <https://docs.djangoproject.com/en/stable/topics/auth/default/#session-invalidation-on-password-change>`_.

``ACCOUNT_LOGOUT_REDIRECT_URL`` (default: ``settings.LOGOUT_REDIRECT_URL or "/"``)
  The URL (or URL name) to return to after the user logs out. Defaults to
  Django's ``LOGOUT_REDIRECT_URL``, unless that is empty, then ``"/"`` is used.

``ACCOUNT_PASSWORD_INPUT_RENDER_VALUE`` (default: ``False``)
  ``render_value`` parameter as passed to ``PasswordInput`` fields.

``ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED`` (default: ``False``)
  Controls whether password reset is performed by means of following a link
  in the email (``False``), or by entering a code (``True``).

``ACCOUNT_PASSWORD_RESET_BY_CODE_MAX_ATTEMPTS`` (default: ``3``)
  This setting controls the maximum number of attempts the user has at inputting
  a valid code.

``ACCOUNT_PASSWORD_RESET_BY_CODE_TIMEOUT`` (default: ``180``)
  The code that is emailed has a limited life span. It expires this many seconds after
  which it was sent.

``ACCOUNT_PASSWORD_RESET_TOKEN_GENERATOR`` (default: ``"allauth.account.forms.EmailAwarePasswordResetTokenGenerator"``)
  A string pointing to a custom token generator
  (e.g. 'myapp.auth.CustomTokenGenerator') for password resets. This class
  should implement the same methods as
  ``django.contrib.auth.tokens.PasswordResetTokenGenerator`` or subclass it.

``ACCOUNT_PRESERVE_USERNAME_CASING`` (default: ``True``)
  This setting determines whether the username is stored in lowercase
  (``False``) or whether its casing is to be preserved (``True``). Note that when
  casing is preserved, potentially expensive ``__iexact`` lookups are performed
  when filter on username. For now, the default is set to ``True`` to maintain
  backwards compatibility.

``ACCOUNT_PREVENT_ENUMERATION`` (default: ``True``)
  Controls whether or not information is revealed about whether or not a user
  account exists. For example, by entering random email addresses in the
  password reset form you can test whether or not those email addresses are
  associated with an account. Enabling this setting prevents that, and an email
  is always sent, regardless of whether or not the account exists. Note that
  there is a slight usability tax to pay because there is no immediate feedback.

  Whether or not enumeration can be prevented during signup depends on the email
  verification method. In case of mandatory verification, enumeration can be
  properly prevented because the case where an email address is already taken is
  indistinguishable from the case where it is not.  However, in case of optional
  or disabled email verification, enumeration can only be prevented by allowing
  the signup to go through, resulting in multiple accounts sharing same email
  address (although only one of the accounts can ever have it verified). When
  enumeration is set to ``True``, email address uniqueness takes precedence over
  enumeration prevention, and the issue of multiple accounts having the same
  email address will be avoided, thus leaking information. Set it to
  ``"strict"`` to allow for signups to go through.

``ACCOUNT_RATE_LIMITS`` (default: ``{...}``)
  In order to be secure out of the box various rate limits are in place.
  See :doc:`Rate Limits <./rate_limits>` for details.

``ACCOUNT_REAUTHENTICATION_TIMEOUT`` (default: ``300``)
  Before asking the user to reauthenticate, we check if a successful
  (re)authentication happened within the amount of seconds specified here, and
  if that is the case, the new reauthentication flow is silently skipped.

``ACCOUNT_REAUTHENTICATION_REQUIRED`` (default: ``False``)
  Specifies whether or not reauthentication is required before the user can
  alter his account.

``ACCOUNT_SESSION_REMEMBER`` (default: ``None``)
  Controls the life time of the session. Set to ``None`` to ask the user
  ("Remember me?"), ``False`` to not remember, and ``True`` to always
  remember.

``ACCOUNT_SIGNUP_FIELDS`` (default: ``['username*', 'email', 'password1*', 'password2*']``)
  The list of fields to complete in the signup form. Fields marked with an
  asterisk (e.g. ``'username*'``) are required.  To let the user type in their
  email address twice to avoid typos, you can add ``'email2'``.  The field
  ``'password2'`` can be used let the user type in their password twice to avoid
  typos.

``ACCOUNT_SIGNUP_FORM_CLASS`` (default: ``None``)
  A string pointing to a custom form class
  (e.g. ``'myapp.forms.SignupForm'``) that is used during signup to ask
  the user for additional input (e.g. newsletter signup, birth
  date). This class should implement a ``def signup(self, request, user)``
  method, where user represents the newly signed up user.

``ACCOUNT_SIGNUP_FORM_HONEYPOT_FIELD`` (default: ``None``)
  A string value that will be used as the HTML 'name' property
  on a honeypot input field on the sign up form. Honeypot fields are hidden
  to normal users but might be filled out by naive spam bots. When the field
  is filled out the app will not create a new user and attempt to fool
  the bot with a fake successful response. We recommend setting this
  to some believable value that your app does not actually collect
  on signup e.g. 'phone_number' or 'address'. Honeypots are not
  always successful for sophisticated bots so this should be
  used as one layer in a suite of spam detection tools if your
  site is having trouble with spam.

``ACCOUNT_SIGNUP_REDIRECT_URL`` (default: ``settings.LOGIN_REDIRECT_URL``)
  The URL (or URL name) to redirect to directly after signing up. Note that
  users are only redirected to this URL if the signup went through
  uninterruptedly, for example, without any side steps due to email
  verification. If your project requires the user to always pass through certain
  onboarding views after signup, you will have to keep track of state indicating
  whether or not the user successfully onboarded, and handle accordingly.

``ACCOUNT_TEMPLATE_EXTENSION`` (default: ``"html"``)
  A string defining the template extension to use, defaults to ``html``.

``ACCOUNT_USERNAME_BLACKLIST`` (default: ``[]``)
  A list of usernames that can't be used by user.

``ACCOUNT_UNIQUE_EMAIL`` (default: ``True``)
  Enforce uniqueness of email addresses. On the database level, this implies
  that only one user account can have an email address marked as verified.
  Forms prevent a user from registering with or adding an additional email
  address if that email address is in use by another account.

``ACCOUNT_USER_DISPLAY`` (default: a callable returning ``user.username``)
  A callable (or string of the form ``'some.module.callable_name'``)
  that takes a user as its only argument and returns the display name
  of the user. The default implementation returns ``user.username``.

``ACCOUNT_USER_MODEL_EMAIL_FIELD`` (default: ``"email"``)
  The name of the field containing the ``email``, if any. See custom
  user models.

``ACCOUNT_USER_MODEL_USERNAME_FIELD`` (default: ``"username"``)
  The name of the field containing the ``username``, if any. See custom
  user models.

``ACCOUNT_USERNAME_MIN_LENGTH`` (default: ``1``)
  An integer specifying the minimum allowed length of a username.

``ACCOUNT_USERNAME_VALIDATORS`` (default: ``None``)
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
