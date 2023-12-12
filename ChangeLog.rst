0.59.0 (2023-12-13)
*******************

Note worthy changes
-------------------

- The MFA authenticator model now features "created at" an "last used "at"
  timestamps.

- The MFA authenticator model is now registered with the Django admin.

- Added MFA signals emitted when authenticators are added, removed or (in case
  of recovery codes) reset.

- There is now an MFA adapter method ``can_delete_authenticator(authenticator)``
  available that can be used to prevent users from deactivating e.g. their TOTP
  authenticator.

- Added a new app, user sessions, allowing users to view a list of all their
  active sessions, as well as offering a means to end these sessions.

- A configurable timeout (``SOCIALACCOUNT_REQUESTS_TIMEOUT``) is now applied to
  all upstream requests.

- Added a setting ``ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS`` to disable sending of
  emails to unknown accounts.

- You can now override the MFA forms via the ``MFA_FORMS`` setting.


Backwards incompatible changes
------------------------------

- The account adapter method ``should_send_confirmation_mail()`` signature
  changed. It now takes an extra ``signup`` (boolean) parameter.

- Removed OAuth 1.0 based Bitbucket provider and LinkedIn provider.


0.58.2 (2023-11-06)
*******************

Fixes
-----

- Added rate limiting to the MFA login form.


0.58.1 (2023-10-29)
*******************

Fixes
-----

- Fixed missing ``{% load allauth %}`` in the login cancelled and verified email
  required template.


0.58.0 (2023-10-26)
*******************

Note worthy changes
-------------------

- The ``SocialAccount.extra_data`` field was a custom JSON field that used
  ``TextField`` as the underlying implementation. It was once needed because
  Django had no ``JSONField`` support. Now, this field is changed to use the
  official ``JSONField()``. Migrations are in place.

- Officially support Django 5.0.

- In previous versions, users could never remove their primary email address.
  This is constraint is now relaxed. In case the email address is not required,
  for example, because the user logs in by username, removal of the email
  address is allowed.

- Added a new setting ``ACCOUNT_REAUTHENTICATION_REQUIRED`` that, when enabled,
  requires the user to reauthenticate before changes (such as changing the
  primary email address, adding a new email address, etc.) can be performed.


Backwards incompatible changes
------------------------------

- Refactored the built-in templates, with the goal of being able to adjust the
  look and feel of the whole project by only overriding a few core templates.
  This approach allows you to achieve visual results fast, but is of course more
  limited compared to styling all templates yourself. If your project provided
  its own templates then this change will not affect anything, but if you rely
  on (some of) the built-in templates your project may be affected.

- The Azure provider has been removed in favor of keeping the Microsoft
  provider. Both providers were targeting the same goal.


Security notice
---------------

- Facebook: Using the JS SDK flow, it was possible to post valid access tokens
  originating from other apps. Facebook user IDs are scoped per app. By default
  that user ID (not the email address) is used as key while
  authenticating. Therefore, such access tokens can not be abused by
  default. However, in case ``SOCIALACCOUNT_EMAIL_AUTHENTICATION`` was
  explicitly enabled for the Facebook provider, these tokens could be used to
  login.


0.57.0 (2023-09-24)
*******************

Note worthy changes
-------------------

- Added Django password validation help text to ``password1`` on
  set/change/signup forms.

- Microsoft: the tenant parameter can now be configured per app.

- SAML: Added support for additional configuration parameters, such as contacts,
  and support for certificate rotation.

- The enumeration prevention behavior at signup is now configurable. Whether or
  not enumeration can be prevented during signup depends on the email
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


Fixes
=====

- Fixed ``?next=`` URL handling in the SAML provider.

- During 2FA, pending logins were incorrectly removed when e.g. Django was asked
  to serve a ``/favicon.ico`` URL.


0.56.1 (2023-09-08)
*******************

Security notice
---------------

- ``ImmediateHttpResponse`` exceptions were not handled properly when raised
  inside ``adapter.pre_login()``.  If you relied on aborting the login using
  this mechanism, that would not work. Most notably, django-allauth-2fa uses
  this approach, resulting in 2FA not being triggered.


0.56.0 (2023-09-07)
*******************

Note worthy changes
-------------------

- Added builtin support for Two-Factor Authentication via the ``allauth.mfa`` app.

- The fact that ``request`` is not available globally has left its mark on the
  code over the years. Some functions get explicitly passed a request, some do
  not, and some constructs have it available both as a parameter and as
  ``self.request``.  As having request available is essential, especially when
  trying to implement adapter hooks, the request has now been made globally
  available via::

    from allauth.core import context
    context.request

- Previously, ``SOCIALACCOUNT_STORE_TOKENS = True`` did not work when the social
  app was configured in the settings instead of in the database. Now, this
  functionality works regardless of how you configure the app.


Backwards incompatible changes
------------------------------

- Dropped support for Django 3.1.

- The ``"allauth.account.middleware.AccountMiddleware"`` middleware is required
  to be present in your ``settings.MIDDLEWARE``.

- Starting from September 1st 2023, CERN upgraded their SSO to a standard OpenID
  Connect based solution. As a result, the previously builtin CERN provider is
  no longer needed and has been removed. Instead, use the regular OpenID Connect
  configuration::

    SOCIALACCOUNT_PROVIDERS = {
        "openid_connect": {
            "APPS": [
                {
                    "provider_id": "cern",
                    "name": "CERN",
                    "client_id": "<insert-id>",
                    "secret": "<insert-secret>",
                    "settings": {
                        "server_url": "https://auth.cern.ch/auth/realms/cern/.well-known/openid-configuration",
                    },
                }
            ]
        }
    }

- The Keycloak provider was added before the OpenID Connect functionality
  landed. Afterwards, the Keycloak implementation was refactored to reuse the
  regular OIDC provider. As this approach led to bugs (see 0.55.1), it was
  decided to remove the Keycloak implementation altogether.  Instead, use the
  regular OpenID Connect configuration::

    SOCIALACCOUNT_PROVIDERS = {
        "openid_connect": {
            "APPS": [
                {
                    "provider_id": "keycloak",
                    "name": "Keycloak",
                    "client_id": "<insert-id>",
                    "secret": "<insert-secret>",
                    "settings": {
                        "server_url": "http://keycloak:8080/realms/master/.well-known/openid-configuration",
                    },
                }
            ]
        }
    }


0.55.2 (2023-08-30)
*******************

Fixes
-----

- Email confirmation: An attribute error could occur when following invalid
  email confirmation links.


0.55.1 (2023-08-30)
*******************

Fixes
-----

- SAML: the lookup of the app (``SocialApp``) was working correctly for apps
  configured via the settings, but failed when the app was configured via the
  Django admin.

- Keycloak: fixed reversal of the callback URL, which was reversed using
  ``"openid_connect_callback"`` instead of ``"keycloak_callback"``. Although the
  resulting URL is the same, it results in a ``NoReverseMatch`` error when
  ``allauth.socialaccount.providers.openid_connect`` is not present in
  ``INSTALLED_APPS``.


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

- Example base template was missing ``{% load i18n %}``, fixed.


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
