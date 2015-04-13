Configuration
=============

Available settings:

ACCOUNT_ADAPTER (="allauth.account.adapter.DefaultAccountAdapter")
  Specifies the adapter class to use, allowing you to alter certain
  default behaviour.

ACCOUNT_AUTHENTICATION_METHOD (="username" | "email" | "username_email")
  Specifies the login method to use -- whether the user logs in by
  entering their username, e-mail address, or either one of both.
  Setting this to "email" requires ACCOUNT_EMAIL_REQUIRED=True

ACCOUNT_CONFIRM_EMAIL_ON_GET (=False)
  Determines whether or not an e-mail address is automatically confirmed
  by a mere GET request.

ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL (=settings.LOGIN_URL)
  The URL to redirect to after a successful e-mail confirmation, in case no
  user is logged in.

ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL (=None)
  The URL to redirect to after a successful e-mail confirmation, in
  case of an authenticated user. Set to `None` to use
  `settings.LOGIN_REDIRECT_URL`.

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS (=3)
  Determines the expiration date of email confirmation mails (# of days).

ACCOUNT_EMAIL_REQUIRED (=False)
  The user is required to hand over an e-mail address when signing up.

ACCOUNT_EMAIL_VERIFICATION (="optional")
  Determines the e-mail verification method during signup -- choose
  one of `"mandatory"`, `"optional"`, or `"none"`. When set to
  "mandatory" the user is blocked from logging in until the email
  address is verified. Choose "optional" or "none" to allow logins
  with an unverified e-mail address. In case of "optional", the e-mail
  verification mail is still sent, whereas in case of "none" no e-mail
  verification mails are sent.

ACCOUNT_EMAIL_SUBJECT_PREFIX (="[Site] ")
  Subject-line prefix to use for email messages sent. By default, the
  name of the current `Site` (`django.contrib.sites`) is used.

ACCOUNT_DEFAULT_HTTP_PROTOCOL = (="http")
  The default protocol used for when generating URLs, e.g. for the
  password forgotten procedure. Note that this is a default only --
  see the section on HTTPS for more information.

ACCOUNT_FORMS (={})
  Used to override forms, for example:
  `{'login': 'myapp.forms.LoginForm'}`

ACCOUNT_LOGOUT_ON_GET (=False)
  Determines whether or not the user is automatically logged out by a
  mere GET request. See documentation for the `LogoutView` for
  details.

ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE (=False)
  Determines whether or not the user is automatically logged out after
  changing the password. See documentation for `Django's session invalidation on password change <https://docs.djangoproject.com/en/1.8/topics/auth/default/#session-invalidation-on-password-change>`_. (Django 1.7+)

ACCOUNT_LOGOUT_REDIRECT_URL (="/")
  The URL (or URL name) to return to after the user logs out. This is
  the counterpart to Django's `LOGIN_REDIRECT_URL`.

ACCOUNT_SIGNUP_FORM_CLASS (=None)
  A string pointing to a custom form class
  (e.g. 'myapp.forms.SignupForm') that is used during signup to ask
  the user for additional input (e.g. newsletter signup, birth
  date). This class should implement a `def signup(self, request, user)`
  method, where user represents the newly signed up user.

ACCOUNT_SIGNUP_PASSWORD_VERIFICATION (=True)
  When signing up, let the user type in their password twice to avoid typo's.

ACCOUNT_UNIQUE_EMAIL (=True)
  Enforce uniqueness of e-mail addresses.

ACCOUNT_USER_MODEL_USERNAME_FIELD (="username")
  The name of the field containing the `username`, if any. See custom
  user models.

ACCOUNT_USER_MODEL_EMAIL_FIELD (="email")
  The name of the field containing the `email`, if any. See custom
  user models.

ACCOUNT_USER_DISPLAY (=a callable returning `user.username`)
  A callable (or string of the form `'some.module.callable_name'`)
  that takes a user as its only argument and returns the display name
  of the user. The default implementation returns `user.username`.

ACCOUNT_USERNAME_MIN_LENGTH (=1)
  An integer specifying the minimum allowed length of a username.

ACCOUNT_USERNAME_BLACKLIST (=[])
  A list of usernames that can't be used by user.

ACCOUNT_USERNAME_REQUIRED (=True)
  The user is required to enter a username when signing up. Note that
  the user will be asked to do so even if
  `ACCOUNT_AUTHENTICATION_METHOD` is set to `email`. Set to `False`
  when you do not wish to prompt the user to enter a username.

ACCOUNT_PASSWORD_INPUT_RENDER_VALUE (=False)
  `render_value` parameter as passed to `PasswordInput` fields.

ACCOUNT_PASSWORD_MIN_LENGTH (=6)
  An integer specifying the minimum password length.

ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION (=True)
  The default behaviour is to automatically log users in once they confirm
  their email address. Note however that this only works when confirming
  the email address **immediately after signing up**, assuming users
  didn't close their browser or used some sort of private browsing mode.

  By changing this setting to `False` they will not be logged in, but
  redirected to the `ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL`

ACCOUNT_SESSION_REMEMBER (=None)
  Controls the life time of the session. Set to `None` to ask the user
  ("Remember me?"), `False` to not remember, and `True` to always
  remember.

ACCOUNT_SESSION_COOKIE_AGE (=1814400)
  How long before the session cookie expires in seconds.  Defaults to 1814400 seconds,
  or 3 weeks.

SOCIALACCOUNT_ADAPTER (="allauth.socialaccount.adapter.DefaultSocialAccountAdapter")
  Specifies the adapter class to use, allowing you to alter certain
  default behaviour.

SOCIALACCOUNT_QUERY_EMAIL (=ACCOUNT_EMAIL_REQUIRED)
  Request e-mail address from 3rd party account provider? E.g. using
  OpenID AX, or the Facebook "email" permission.

SOCIALACCOUNT_AUTO_SIGNUP (=True)
  Attempt to bypass the signup form by using fields (e.g. username,
  email) retrieved from the social account provider. If a conflict
  arises due to a duplicate e-mail address the signup form will still
  kick in.

SOCIALACCOUNT_EMAIL_REQUIRED (=ACCOUNT_EMAIL_REQUIRED)
  The user is required to hand over an e-mail address when signing up
  using a social account.

SOCIALACCOUNT_EMAIL_VERIFICATION (=ACCOUNT_EMAIL_VERIFICATION)
  As `ACCOUNT_EMAIL_VERIFICATION`, but for social accounts.

SOCIALACCOUNT_FORMS (={})
  Used to override forms, for example:
  `{'signup': 'myapp.forms.SignupForm'}`

SOCIALACCOUNT_PROVIDERS (= dict)
  Dictionary containing provider specific settings.

SOCIALACCOUNT_STORE_TOKENS (=True)
  Indicates whether or not the access tokens are stored in the database.
