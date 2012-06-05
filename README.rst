==============
Django AllAuth
==============

Integrated set of Django applications addressing authentication,
registration, account management as well as 3rd party (social) account
authentication.

Overview
========

Supported Flows
***************

- Signup of a both local and social accounts

- Connecting more than one social account to a local account

- Disconnecting a social account -- requires setting a password if
  only the local account remains

- Optional instant-signup for social accounts -- no questions asked

- E-mail address management (multiple e-mail addresses, setting a primary)

- Password forgotten flow

- E-mail address verification flow

Supported Providers
*******************

- Facebook

- Github

- LinkedIn

- OpenId

- Twitter

Note: OAuth/OAuth2 support is built using a common code base, making it easy to add support for additional OAuth/OAuth2 providers. More will follow soon...

 
Features
********

- Supports multiple authentication schemes (e.g. login by user name,
  or by e-mail), as well as multiple strategies for account
  verification (ranging from none to e-mail verification).

- Facebook access token is stored so that you can publish wall updates
  etc.

Architecture & Design
*********************

- Pluggable signup form for asking additional questions during signup.

- Support for connecting multiple social accounts to a Django user account.

- The required consumer keys and secrets for interacting with
  Facebook, Twitter and the likes are to be configured in the database
  via the Django admin using the SocialApp model.

- Consumer keys, tokens make use of the Django sites framework. This
  is especially helpful for larger multi-domain projects, but also
  allows for for easy switching between a development (localhost) and
  production setup without messing with your settings and database.


Installation
============

Django
******

settings.py::

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        "allauth.context_processors.allauth",
        "allauth.account.context_processors.account"
    )

    AUTHENTICATION_BACKENDS = ( ...
        "allauth.account.auth_backends.AuthenticationBackend", )

    INSTALLED_APPS = (
        ...
        'emailconfirmation',

        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.socialaccount.providers.twitter',
        'allauth.socialaccount.providers.linkedin',
        'allauth.socialaccount.providers.openid',
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.github',

urls.py::

    urlpatterns = patterns('',
        ...
        (r'^accounts/', include('allauth.urls')))


Configuration
*************

Available settings:

ACCOUNT_EMAIL_REQUIRED (=False)
  The user is required to hand over an e-mail address when signing up.

ACCOUNT_EMAIL_VERIFICATION (=False)
  After signing up, keep the user account inactive until the e-mail
  address is verified.

ACCOUNT_EMAIL_AUTHENTICATION (=False)
  Login by e-mail address, not username.

ACCOUNT_EMAIL_SUBJECT_PREFIX (="[Site] ")
  Subject-line prefix to use for email messages sent. By default, the
  name of the current `Site` (`django.contrib.sites`) is used.

ACCOUNT_SIGNUP_FORM_CLASS (=None)
  A string pointing to a custom form class
  (e.g. 'myapp.forms.SignupForm') that is used during signup to ask
  the user for additional input (e.g. newsletter signup, birth
  date). This class should implement a 'save' method, accepting the
  newly signed up user as its only parameter.

ACCOUNT_SIGNUP_PASSWORD_VERIFICATION (=True)
  When signing up, let the user type in his password twice to avoid typ-o's.

ACCOUNT_UNIQUE_EMAIL (=True)
  Enforce uniqueness of e-mail addresses.

ACCOUNT_USERNAME_REQUIRED (=True)
  If false, generates a random username rather than prompting for one
  at signup.

ACCOUNT_PASSWORD_INPUT_RENDER_VALUE (=False)
  `render_value` parameter as passed to `PasswordInput` fields.

SOCIALACCOUNT_QUERY_EMAIL (=ACCOUNT_EMAIL_REQUIRED)
  Request e-mail address from 3rd party account provider? E.g. using
  OpenID AX, or the Facebook "email" permission.

SOCIALACCOUNT_AUTO_SIGNUP (=True) 
  Attempt to bypass the signup form by using fields (e.g. username,
  email) retrieved from the social account provider. If a conflict
  arises due to a duplicate e-mail address the signup form will still
  kick in.

SOCIALACCOUNT_AVATAR_SUPPORT (= 'avatar' in settings.INSTALLED_APPS)
  Enable support for django-avatar. When enabled, the profile image of
  the user is copied locally into django-avatar at signup.

EMAIL_CONFIRMATION_DAYS (=# of days, no default)
  Determines the expiration date of email confirmation mails sent by
  django-email-confirmation.

