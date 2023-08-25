0.56.0 (unreleased)
*******************

Note worthy changes
-------------------

- ...


Backwards incompatible changes
------------------------------

- Dropped support for Django 3.1.


0.55.0 (2023-08-22)
*******************

Note worthy changes
-------------------

- Introduced a new setting ``ACCOUNT_PASSWORD_RESET_TOKEN_GENERATOR`` that
  allows you to specify the token generator for password resets.

- Dropped support for Django 2.x and 3.0.

- Officially support Django 4.2.

- New providers: Miro, Questrade

- It is now possible to manage OpenID Connect providers via the Django
  admin. Simply add a `SocialApp` for each OpenID Connect provider.

- There is now a new flow for changing the email address. When enabled
  (``ACCOUNT_CHANGE_EMAIL``), users are limited to having exactly one email
  address that they can change by adding a temporary second email address that,
  when verified, replaces the current email address.

- Changed spelling from "e-mail" to "email". Both are correct, however, the
  trend over the years has been towards the simpler and more streamlined form
  "email".

- Added support for SAML 2.0. Thanks to `Dskrpt <https://dskrpt.de>`_
  for sponsoring the development of this feature!

- Fixed Twitter OAuth2 authentication by using basic auth and adding scope `tweet.read`.

- Added (optional) support for authentication by email for social logins (see
  ``SOCIALACCOUNT_EMAIL_AUTHENTICATION``).


Security notice
---------------

- Even with account enumeration prevention in place, it was possible for a user
  to infer whether or not a given account exists based by trying to add
  secondary email addresses .  This has been fixed -- see the note on backwards
  incompatible changes.


Backwards incompatible changes
------------------------------

- Data model changes: when ``ACCOUNT_UNIQUE_EMAIL=True`` (the default), there
  was a unique constraint on set on the ``email`` field of the ``EmailAddress``
  model. This constraint has been relaxed, now there is a unique constraint on
  the combination of ``email`` and ``verified=True``. Migrations are in place to
  automatically transition, but if you have a lot of accounts, you may need to
  take special care using ``CREATE INDEX CONCURRENTLY``.

- The method ``allauth.utils.email_address_exists()`` has been removed.

- The Mozilla Persona provider has been removed. The project was shut down on
  November 30th 2016.

- A large internal refactor has been performed to be able to add support for
  providers oferring one or more subproviders. This refactor has the following
  impact:

  - The provider registry methods ``get_list()``, ``by_id()`` have been
    removed. The registry now only providers access to the provider classes, not
    the instances.

  - ``provider.get_app()`` has been removed -- use ``provider.app`` instead.

  - ``SocialApp.objects.get_current()`` has been removed.

  - The ``SocialApp`` model now has additional fields ``provider_id``, and
    ``settings``.

  - The OpenID Connect provider ``SOCIALACCOUNT_PROVIDERS`` settings structure
    changed.  Instead of the OpenID Connect specific ``SERVERS`` construct, it
    now uses the regular ``APPS`` approach. Please refer to the OpenID Connect
    provider documentation for details.

  - The Telegram provider settings structure, it now requires to app. Please
    refer to the Telegram provider documentation for details.

- The Facebook provider loaded the Facebook connect ``sdk.js`` regardless of the
  value of the ``METHOD`` setting. To prevent tracking, now it only loads the
  Javascript if ``METHOD`` is explicitly set to ``"js_sdk"``.



0.54.0 (2023-03-31)
*******************

Note worthy changes
-------------------

- Dropped support for EOL Python versions (3.5, 3.6).


Security notice
---------------

- Even when account enumeration prevention was turned on, it was possible for an
  attacker to infer whether or not a given account exists based upon the
  response time of an authentication attempt. Fixed.


0.53.1 (2023-03-20)
*******************

Note worthy changes
-------------------

- Example base template was missing ``{% load i18n}``, fixed.


0.53.0 (2023-03-16)
*******************

Note worthy changes
-------------------

- You can now override the use of the ``UserTokenForm`` over at the
  ``PasswordResetFromKeyView`` by configuring ``ACCOUNT_FORMS["user_token"]`` to
  allow the change of the password reset token generator.

- The Google API URLs are now configurable via the provider setting which
  enables use-cases such as overriding the endpoint during integration tests to
  talk to a mocked version of the API.


0.52.0 (2022-12-29)
*******************

Note worthy changes
-------------------

- Officially support Django 4.1.

- New providers: OpenID Connect, Twitter (OAuth2), Wahoo, DingTalk.

- Introduced a new provider setting ``OAUTH_PKCE_ENABLED`` that enables the
  PKCE-enhanced Authorization Code Flow for OAuth 2.0 providers.

- When ``ACCOUNT_PREVENT_ENUMERATION`` is turned on, enumeration is now also
  prevented during signup, provided you are using mandatory email
  verification. There is a new email template
  (`templates/account/email/acccount_already_exists_message.txt`) that will be
  used in this scenario.

- Updated URLs of Google's endpoints to the latest version; removed a redundant
  ``userinfo`` call.

- Fixed Pinterest provider on new api version.


0.51.0 (2022-06-07)
*******************

Note worthy changes
-------------------

- New providers: Snapchat, Hubspot, Pocket, Clever.


Security notice
---------------

The reset password form is protected by rate limits. There is a limit per IP,
and per email. In previous versions, the latter rate limit could be bypassed by
changing the casing of the email address. Note that in that case, the former
rate limit would still kick in.


0.50.0 (2022-03-25)
*******************

Note worthy changes
-------------------

- Fixed compatibility issue with setuptools 61.

- New providers: Drip.

- The Facebook API version now defaults to v13.0.


0.49.0 (2022-02-22)
*******************

Note worthy changes
-------------------

- New providers: LemonLDAP::NG.

- Fixed ``SignupForm`` setting username and email attributes on the ``User`` class
  instead of a dummy user instance.

- Email addresses POST'ed to the email management view (done in order to resend
  the confirmation email) were not properly validated. Yet, these email
  addresses were still added as secondary email addresses. Given the lack of
  proper validation, invalid email addresses could have entered the database.

- New translations: Romanian.


Backwards incompatible changes
------------------------------

- The Microsoft ``tenant`` setting must now be specified using uppercase ``TENANT``.

- Changed naming of ``internal_reset_url_key`` attribute in
  ``allauth.account.views.PasswordResetFromKeyView`` to ``reset_url_key``.


0.48.0 (2022-02-03)
*******************

Note worthy changes
-------------------
- New translations: Catalan, Bulgarian.

- Introduced a new setting ``ACCOUNT_PREVENT_ENUMERATION`` that controls whether
  or not information is revealed about whether or not a user account exists.
  **Warning**: this is a work in progress, password reset is covered, yet,
  signing up is not.

- The ``ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN`` is now also respected when using
  HMAC based email confirmations. In earlier versions, users could trigger email
  verification mails without any limits.

- Added builtin rate limiting (see ``ACCOUNT_RATE_LIMITS``).

- Added ``internal_reset_url_key`` attribute in
  ``allauth.account.views.PasswordResetFromKeyView`` which allows specifying
  a token parameter displayed as a component of password reset URLs.

- It is now possible to use allauth without having ``sites`` installed. Whether or
  not sites is used affects the data models. For example, the social app model
  uses a many-to-many pointing to the sites model if the ``sites`` app is
  installed. Therefore, enabling or disabling ``sites`` is not something you can
  do on the fly.

- The ``facebook`` provider no longer raises ``ImproperlyConfigured``
  within ``{% providers_media_js %}`` when it is not configured.


Backwards incompatible changes
------------------------------

- The newly introduced ``ACCOUNT_PREVENT_ENUMERATION`` defaults to ``True`` impacting
  the current behavior of the password reset flow.

- The newly introduced rate limiting is by default turned on. You will need to provide
  a ``429.html`` template.

- The default of ``SOCIALACCOUNT_STORE_TOKENS`` has been changed to
  ``False``. Rationale is that storing sensitive information should be opt in, not
  opt out. If you were relying on this functionality without having it
  explicitly turned on, please add it to your ``settings.py``.
