65.14.0 (2026-01-17)
********************

Note worthy changes
-------------------

- Steam: the provider now supports initiating headless logins per
  redirect.

- Shopify: if ``email_verified`` is present in the user payload, it will be used
  to mark the email address retrieved as verified accordingly.

- IdP: added support for JWT based access tokens (see
  ``IDP_OIDC_ACCESS_TOKEN_FORMAT``).

- IdP: added support for pointing to a custom userinfo endpoint (see
  ``IDP_OIDC_USERINFO_ENDPOINT``)

- For OpenID Connect providers, you can now configure the field to be used as
  the account ID by setting ``"uid_field"`` in the relevant
  ``SocialApp.settings``.

- Headless: the JWT algorithm is now configurable, supporting HS256.


Fixes
-----

- IdP: Access tokens without a user attached (client credentials) were no longer
  recognized in DRF/Ninja endpoints.

- ``requests`` sessions are now disposed of after use to avoid resource leaks.


65.13.1 (2025-11-20)
********************

Note worthy changes
-------------------

- Django 6.0 is now officially supported.


Fixes
-----

- Internal imports related to headless token strategies were causing (harmless)
  deprecation warnings, fixed.

- Pending social signups stored in the session by allauth versions prior to
  65.5.0 are not resumable by newer versions. This could cause 500s while
  upgrading, fixed.

- Headless: the reauthentication-required response in the OpenAPI specification
  was wrongly nested and did not match the actual implementation, fixed.


65.13.0 (2025-10-31)
********************

Note worthy changes
-------------------

- IdP: Added support for RP-Initiated Logout.

- Headless: added JWT token strategy.

- Added support for "Trust this browser?" functionality for logging in by code.
  See ``ACCOUNT_LOGIN_BY_CODE_TRUST_ENABLED``.

- OpenID Connect: to avoid issues with client IDs containing colons,
  ``client_secret_post`` is now preferred above ``client_secret_basic``.


Security notice
---------------

- Both Okta and NetIQ were using ``preferred_username`` as the identifier for
  third-party provider accounts.  That value may be mutable and should therefore
  be avoided for authorization decisions.  The providers are now using ``sub``
  instead.

- IdP: marking a user as ``is_active=False`` after having handed tokens for that
  user while the account was still active had no effect. Fixed -- the
  access/refresh tokens are now rejected. Thanks to Joshua Rogers for reporting
  this and the previous issue.


Backwards incompatible changes
------------------------------

- Headless now requires the ``headless`` extra to be installed. For example:
  ``pip install django-allauth[headless]``.

- Okta and NetIQ: see the security notice on Okta and NetIQ. Already existing
  ``SocialAccount`` records will no longer be linked due to the switch to
  ``sub``.  You will need to manually handle this situation either, by
  populating ``SocialAccount.uid`` based on ``sub`` located in
  ``SocialAccount.extra_data``,or, if you are absolutely certain the security
  notice is of no concern for your use case, by setting ``"uid_field":
  "preferred_username"`` in the relevant ``SocialApp.settings``.


65.12.1 (2025-10-16)
********************

Security notice
---------------

- There was a flaw in the email verification process when using
  ``ACCOUNT_CHANGE_EMAIL = True``.  If you are using this configuration, you are
  advised to upgrade as soon as possible.  Note that the default value is
  ``False``.


65.12.0 (2025-10-05)
********************

Note worthy changes
-------------------

- Updated VK urls from "vk.com" to "vk.ru".

- Added new socialaccount provider: Discogs.

- MediaWiki: you can now setup a custom user agent to avoid getting blocked,
  see: https://phabricator.wikimedia.org/T400119

- IdP: Added optional support for wildcards in redirect URIs and CORS origins.
  To support this, a new field was added to the ``Client`` model. Therefore, you
  need to run migrations for the ``allauth.idp.oidc`` app.

- Headless: an email address that was in the process of being verified by code
  was presented in the list of email address, but could not be deleted. Now, a
  ``DELETE`` will actually abort the process, effectively removing the pending
  email address from the list.


65.11.2 (2025-09-09)
********************

Fixes
-----

- OpenID Connect: the OpenID Connect provider was using the wrong key lookup
  mechanism, resulting in login failures.


65.11.1 (2025-08-27)
********************

Security notice
---------------

- If you configured password to be optional (e.g. using ``ACCOUNT_SIGNUP_FIELDS
  = ["email*", "password1"]``), then accounts would be created having a blank
  password instead of an unusable password. If you were using this configuration
  then you may need to manually set an unusable password for accounts created.


65.11.0 (2025-08-15)
********************

Note worthy changes
-------------------

- OpenID Connect: using ``fetch_userinfo=False`` you can now skip the additional
  call to the userinfo endpoint. Instead, the ID token will be used.


Fixes
-----

- Headless: passwordless signup was not supported, fixed.

- Headless: when serializing the user nested dataclasses, as well as optional
  types ended up as ``string`` type, fixed.

- When signing up with a social account no authentication record was added to
  the session, fixed.


Backwards incompatible changes
------------------------------

- OpenID Connect: the ID token and userinfo (when present) are now stored in
  ``SocialAccount.extra_data``, below the respective ``"id_token"`` and
  ``"userinfo"`` keys. Compatibility with ``extra_data`` from existing accounts
  that do not have this new structure is retained. However, if your own project
  expects ``extra_data`` to be in a certain format this change may impact you.


65.10.0 (2025-07-10)
********************

Note worthy changes
-------------------

- IdP: Added support for the device authorization grant.

- Headless: custom user payloads can now be properly reflected in the OpenAPI
  specification by provider a user ``dataclass``. See the newly introduced
  ``get_user_dataclass()`` and ``user_as_dataclass()`` adapter methods.

- Added a new signal (``authentication_step_completed``) that is emitted when an
  individual authentication step is completed.

- MFA: Added a setting (``MFA_ALLOW_UNVERIFIED_EMAIL``) to allow unverified
  email addresses in combination with MFA.


Backwards incompatible changes
------------------------------

- Soundcloud: as per https://developers.soundcloud.com/blog/urn-num-to-string,
  the provider now uses the user ``urn`` instead of the ``id`` as the ID for
  social accounts. This change is backward incompatible. Instructions on
  how to migrate existing social accounts can be found in the allauth provider
  documentation for SoundCloud.


Fixes
-----

- Phone: The recently added support for phone (SMS) authentication did fully integrate
  with third-party provider signups. For example, whether or not the phone
  number is required was not respected during signup. Fixed.

- IdP: Token revocation failed when a single ``token_type_hint`` was passed,
  fixed.

- The ``verified_email_required`` decorator did not support email verification
  by code. Additionally, it did not rate limit verification emails
  in case of GET requests. Both are fixed.

- The account adapter ``clean_email()`` method was not called when a social account
  auto signup took place, fixed.


65.9.0 (2025-06-01)
*******************

Note worthy changes
-------------------

- Added ``allauth.idp`` to the project, offering out of the box OpenID Connect
  provider support, as well as integration with Django REST framework and Django
  Ninja.

- Headless: the OpenAPI specification now more accurately reflects single client
  configurations set via ``HEADLESS_CLIENTS``. When a single client is active,
  the redundant ``{client}`` path parameter and its global definition are
  removed from the generated schema.


65.8.1 (2025-05-21)
*******************

Fixes
-----

- Fixed a compatibility issue with the newly released fido2 2.0.0 package.


Security notice
---------------

- After a successful login, the rate limits for that login were cleared,
  allowing a succesful login on a specific IP address to be used as a means to
  clear the login failed rate limit for that IP address. Fixed.


65.8.0 (2025-05-08)
*******************

Note worthy changes
-------------------

- Fixed VK (a.k.a VK ID) social account provider. Improved its documentation.

- Added optional support for requesting new email/phone verification codes during
  signup.  See ``ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND`` and
  ``ACCOUNT_PHONE_VERIFICATION_SUPPORTS_RESEND``.

- Added optional support for changing your email or phone at the verification stage while signing up.
  See ``ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_CHANGE`` and
  ``ACCOUNT_PHONE_VERIFICATION_SUPPORTS_CHANGE``.

- Added support for Mailcow OAuth2.


65.7.0 (2025-04-03)
*******************

Note worthy changes
-------------------

- Officially support Django 5.2.

- Headless: the URL to the OpenID configuration of the provider is now exposed
  in the provider configuration.


Fixes
-----

- Headless: when multiple login methods were enabled (e.g. both username and
  email), the login endpoint would incorrectly return a 400
  ``invalid_login``. Fixed.


65.6.0 (2025-03-27)
*******************

Note worthy changes
-------------------

- MFA: Added support for "Trust this browser?" functionality, which presents users with MFA
  enabled the choice to trust their browser allowing them to skip authenticating
  per MFA on each login.


Fixes
-----

- A check is in place to verify that ``ACCOUNT_LOGIN_METHODS`` is aligned with
  ``ACCOUNT_SIGNUP_FIELDS``.  The severity level of that check has now been
  lowered from "critical" to "warning", as there may be valid use cases for
  configuring a login method that you are not able to sign up with. This check
  (``account.W001``) can be silenced using Django's ``SILENCED_SYSTEM_CHECKS``.

- The setting ``ACCOUNT_LOGIN_ON_PASSWORD_RESET = True`` was not respected when using
  password reset by code.


65.5.0 (2025-03-14)
*******************

Note worthy changes
-------------------

- Added support for phone (SMS) authentication.

- Added support for resetting passwords by code, instead of a link
  (``ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED``).

- Added support for Tumblr OAuth2.

- Simplified signup form configuration. The following settings all controlled
  signup form: ``ACCOUNT_EMAIL_REQUIRED``, ``ACCOUNT_USERNAME_REQUIRED``,
  ``ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE``, ``ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE``.
  This setup had its issues. For example, when email was not required it was
  still available as an optional field, whereas the username field disappeared
  when not required. Also, for phone/SMS support, additional settings
  would have been required.  The settings are now all deprecated, and replaced by one
  new setting: ``ACCOUNT_SIGNUP_FIELDS``, which can be configured to
  e.g. ``['username*', 'email', 'password1*', 'password2*']`` to indicate which
  fields are present and required (``'*'``). This change is performed in a
  backwards compatible manner.

- Headless: if, while signing up using a third-party provider account, there is
  insufficient information received from the provider to automatically complete
  the signup process, an additional step is needed to complete the missing data
  before the user is fully signed up and authenticated.  You can now perform a
  ``GET`` request to ``/_allauth/{client}/v1/auth/provider/signup`` to obtain
  information on the pending signup.

- Headless: OpenID Connect providers now support token authentication.

- The "Forgot your password?" help text can now be more easily customized by
  providing your own ``"account/password_reset_help_text.html"`` template.

- Removed inline scripts, so that it becomes possible to use a strong Content
  Security Policy.

- Headless: The OpenAPI specification now dynamically reflects the
  ``ACCOUNT_SIGNUP_FIELDS`` configuration, as well as any custom fields you have
  in ``ACCOUNT_SIGNUP_FORM_CLASS``.

- Added official support for Python 3.13.


Fixes
-----

- Headless: In case you had multiple apps of the same provider configured,
  you could run into a ``MultipleObjectsReturned``. Fixed.


65.4.1 (2025-02-07)
*******************

Fixes
-----

- To make way for a future ``"phone"`` method, ``AUTHENTICATION_METHOD`` was
  removed in favor of a new ``LOGIN_METHODS``. While this change was done in a
  backwards compatible manner within allauth scope, other packages accessing
  ``allauth.account.app_settings.AUTHENTICATION_METHOD`` would break. Fixed.


65.4.0 (2025-02-06)
*******************

Note worthy changes
-------------------

- The setting ``ACCOUNT_AUTHENTICATION_METHOD: str`` (with values
  ``"username"``, ``"username_email"``, ``"email"``) has been replaced by
  ``ACCOUNT_LOGIN_METHODS: set[str]``. which is a set of values including
  ``"username"`` or ``"email"``. This change is performed in a backwards
  compatible manner.

- Headless: when ``HEADLESS_SERVE_SPECIFICATION`` is set to ``True``, the API
  specification will be served dynamically, over at
  ``/_allauth/openapi.(yaml|json|html)``.  The
  ``HEADLESS_SPECIFICATION_TEMPLATE_NAME`` can be configured to choose between
  Redoc (``"headless/spec/redoc_cdn.html"``) and Swagger (
  (``"headless/spec/swagger_cdn.html"``).

- Headless: added a new setting, ``HEADLESS_CLIENTS`` which you can use to limit
  the types of API clients (app/browser).

- Headless: expanded the React SPA example to showcase integration with
  Django Ninja as well as Django REST framework.

- Headless: added out of the box support for being able to use the headless
  session tokens with Django Ninja and Django REST framework.
