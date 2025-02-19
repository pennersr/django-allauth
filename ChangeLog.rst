65.5.0 (unreleased)
*******************

Note worthy changes
-------------------

- Added support for resetting passwords by code, instead of a link.

- Simplified signup form configuration. The following settings all controlled
  signup form: ``ACCOUNT_EMAIL_REQUIRED``, ``ACCOUNT_USERNAME_REQUIRED``,
  ``ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE``, ``ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE``.
  This setup had its issues. For example, when email was not required it was
  still available as an optional field, whereas the username field disappeared
  when not required. Also, for future phone/SMS support, additional settings
  would be required.  The settings are now all deprecated, and replaced by one
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


65.3.1 (2024-12-25)
*******************

Fixes
-----

- Headless: When using email verification by code, you could incorrectly
  encounter a 409 when attempting to add a new email address while logged in.

- Headless: In contrast to the headed version, it was possible to remove the
  last 3rd party account from a user that has no usable password. Fixed.

- Headless: The setting ``ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION`` was not respected,
  and always assumed to be ``True``.


65.3.0 (2024-11-30)
*******************

Note worthy changes
-------------------

- Added support for TOTP code tolerance (see ``MFA_TOTP_TOLERANCE``).


Security notice
---------------

- Authentication by email/password was vulnerable to account enumeration by
  means of a timing attack. Thanks to Julie Rymer for the report and the patch.


65.2.0 (2024-11-08)
*******************

Note worthy changes
-------------------

- OIDC: You can now configure whether or not PKCE is enabled per app by
  including ``"oauth_pkce_enabled": True`` in the app settings.

- The OpenStreetMap provider is deprecated. You can set it up as an OpenID Connect provider instead.


Fixes
-----

- A ``NoReverseMatch`` could occur when using ``ACCOUNT_LOGIN_BY_CODE_REQUIRED =
  True`` while ``ACCOUNT_LOGIN_BY_CODE_ENABLED = False``, fixed.

- The ``PasswordResetDoneView`` did not behave correctly when using Django's
  ``LoginRequiredMiddleware``, as it was not properly marked as
  ``@login_not_required``.

- When verifying an email address by code, the success URL was hardcoded to the
  email management view, instead of calling the
  ``get_email_verification_redirect_url()`` adapter method.


Security notice
---------------

- Headless: ``settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS`` was not
  enforced, fixed.  Note that the related verification endpoint will return a
  409 in case the maximum limit is exceeded, as at that point the pending email
  verification stage is aborted.


65.1.0 (2024-10-23)
*******************

Note worthy changes
-------------------

- OAuth2/OIDC: When setting up multiple apps for the same provider, you can now
  configure a different scope per app by including ``"scope": [...]`` in the app
  settings.

- Facebook login: Facebook `Limited Login
  <https://developers.facebook.com/docs/facebook-login/limited-login>`_ is now
  supported via the Headless API. When you have a Limited Login JWT obtained
  from the iOS SDK, you can use the Headless "provider token" flow to login with
  it.


Fixes
-----

- When using ``HEADLESS_ONLY = True`` together with
  ``ACCOUNT_REAUTHENTICATION_REQUIRED = True``, you could run into a
  ``NoReverseMatch`` when connecting a social acount. Fixed.

- In headless mode, submitting a login code when the login flow expired resulted
  in a 500. Fixed -- it now returns a 409.


65.0.2 (2024-09-27)
*******************

Fixes
-----

- A regression occurred in the newly introduced support using
  ``LoginRequiredMiddleware``, fixed.

- For email verification by link, it is not an issue if the user runs into rate
  limits. The reason is that the link is session independent. Therefore, if the
  user hits rate limits, we can just silently skip sending additional
  verification emails, as the previous emails that were already sent still
  contain valid links. This is different from email verification by code.  Here,
  the session contains a specific code, meaning, silently skipping new
  verification emails is not an option, and we must block the login instead. The
  latter was missing, fixed.


65.0.1 (2024-09-23)
*******************

Fixes
-----

- When email verification by code was used, adding additional email addresses
  over at the email management page fired the ``email_added`` signal prematurely
  as the email address instance was still unsaved. Fixed.

- The newly introduced logic to redirect to pending login stages has now been
  integrated in the ``RedirectAuthenticatedUserMixin`` so that the existing
  behavior of invoking ``get_authenticated_redirect_url()`` when already
  authenticated is respected.


65.0.0 (2024-09-22)
*******************

Note worthy changes
-------------------

- Added transparent support for Django's ``LoginRequiredMiddleware`` (new since
  Django 5.1).

- The ``usersessions`` app now emits signals when either the IP address or user
  agent for a session changes.

- Added support for signup using a passkey. See
  ``settings.MFA_PASSKEY_SIGNUP_ENABLED``.


Backwards incompatible changes
------------------------------

- When the user is partially logged in (e.g. pending 2FA, or login by code),
  accessing the login/signup page now redirects to the pending login stage. This
  is similar to the redirect that was already in place when the user was fully
  authenticated while accessing the login/signup page. As a result, cancelling
  (logging out of) the pending stage requires an actual logout POST instead of
  merely linking back to e.g. the login page. The builtin templates handle this
  change transparently, but if you copied any of the templates involving the
  login stages you will have to adjust the cancel link into a logout POST.


64.2.1 (2024-09-05)
*******************

Fixes
-----

- Verifying the email address by clicking on the link would no longer log you in, even
  in case of ``ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True``.


Security notice
---------------

- It was already the case that you could not enable TOTP 2FA if your account had
  unverified email addresses. This is necessary to stop a user from claiming
  email addresses and locking other users out. This safety check is now added to
  WebAuthn security keys as well.

- In case a user signs in into an account using social account email
  authentication (``SOCIALACCOUNT_EMAIL_AUTHENTICATION``) and the email used is
  not verified, the password of the account is now wiped (made unusable) to
  prevent the person that created the account (without verifying it) from
  signing in.


64.2.0 (2024-08-30)
*******************

Note worthy changes
-------------------

- Verifying email addresses by means of a code (instead of a link) is now supported.
  See ``settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED``.

- Added support for requiring logging in by code, so that every user logging in
  is required to input a login confirmation code sent by email. See
  ``settings.ACCOUNT_LOGIN_BY_CODE_REQUIRED``.


Security notice
---------------

- In case an ID token is used for authentication, the JTI is now respected to
  prevent the possibility of replays instead of solely relying on the expiration
  time.


64.1.0 (2024-08-15)
*******************

Note worthy changes
-------------------

- Headless: When trying to login while a user is already logged in, you now get
  a 409.

- Limited the maximum allowed time for a login to go through the various login
  stages. This limits, for example, the time span that the 2FA stage remains
  available. See ``settings.ACCOUNT_LOGIN_TIMEOUT``.


Security notice
---------------

- Headless: When a user was not fully logged in, for example, because (s)he was
  in the process of completing the 2FA process, calling logout would not wipe
  the session containing the partially logged in user.


64.0.0 (2024-07-31)
*******************

Note worthy changes
-------------------

- The 0.x.y version numbers really did not do justice to the state of the
  project, and we are way past the point where a version 1.0 would be
  applicable. Additionally, 64 is a nice round number. Therefore, the version
  numbering is changed from 0.x.y to x.y.z. We will use a loose form of semantic
  versioning. However, please be aware that feature releases may occasionally
  include minor documented backwards incompatibilities. Always read the release
  notes before upgrading.

- Added support for WebAuthn based security keys and passkey login. Note that
  this is currently disabled by default.

- Headless: The TOTP URI is now available in the MFA activation response.

- Headless: When trying to sign up while a user is already logged in, you now get
  a 409.

- Headless: You can now alter the user data payload by overriding the newly
  introduced ``serialize_user()`` adapter method.

- Headless: The token strategy now allows for exposing refresh tokens and any
  other information you may need (such as e.g. ``expires_in``).

- Ensured that email address, given name and family name fields are stored in
  the SocialAccount instance. This information was not previously saved in
  Amazon Cognito, Edmodo, and MediaWiki SocialAccount instances.

- When multiple third-party accounts of the same provider were connected, the
  third-party account connections overview did not always provide a clear
  recognizable distinction between those accounts. Now, the
  ``SocialAccount.__str__()`` has been altered to return the unique username or
  email address, rather than a non-unique display name.


Backwards incompatible changes
------------------------------

- Dropped support for Django 3.2, 4.0 and 4.1 (which all reached end of life).
  As Django 3.2 was the last to support Python 3.7, support for Python 3.7 is
  now dropped as well.


0.63.6 (2024-07-12)
*******************

Security notice
---------------

- When the Facebook provider was configured to use the ``js_sdk`` method the
  login page could become vulnerable to an XSS attack.


0.63.5 (2024-07-11)
*******************

Fixes
-----

- The security fix in 0.63.4 that altered the ``__str__()`` of ``SocialToken``
  caused issues within the Amazon Cognito, Atlassian, JupyterHub, LemonLDAP,
  Nextcloud and OpenID Connect providers. Fixed.


0.63.4 (2024-07-10)
*******************

Security notice
---------------

- The ``__str__()`` method of the ``SocialToken`` model returned the access
  token. As a consequence, logging or printing tokens otherwise would expose the
  access token. Now, the method no longer returns the token. If you want to
  log/print tokens, you will now have to explicitly log the ``token`` field of
  the ``SocialToken`` instance.

- Enumeration prevention: the behavior on the outside of an actual signup versus
  a signup where the user already existed was not fully identical, fixed.


0.63.3 (2024-05-31)
*******************

Note worthy changes
-------------------

- In ``HEADLESS_ONLY`` mode, the ``/accounts/<provider>/login/`` URLs were still
  available, fixed.

- The few remaining OAuth 1.0 providers were not compatible with headless mode,
  fixed.

- Depending on where you placed the ``secure_admin_login(admin.site.login)``
  protection you could run into circular import errors, fixed.


Backwards incompatible changes
------------------------------

- SAML: IdP initiated SSO is disabled by default, see security notice below.


Security notice
---------------

- SAML: ``RelayState`` was used to keep track of whether or not the login flow
  was IdP or SP initiated. As ``RelayState`` is a separate field, not part of
  the ``SAMLResponse`` payload, it is not signed and thereby making the SAML
  login flow vulnerable to CSRF/replay attacks. Now, ``InResponseTo`` is used
  instead, addressing the issue for SP initiated SSO flows. IdP initiated SSO
  remains inherently insecure, by design. For that reason, it is now disabled by
  default. If you need to support IdP initiated SSO, you will need to opt-in to
  that by adding ``"reject_idp_initiated_sso": False`` to your advanced SAML
  provider settings.


0.63.2 (2024-05-24)
*******************

Note worthy changes
-------------------

- ``allauth.headless`` now supports the ``is_open_for_signup()`` adapter method.
  In case signup is closed, a 403 is returned during signup.

- Connecting a third-party account in ``HEADLESS_ONLY`` mode failed if the
  connections view could not be reversed, fixed.

- In case a headless attempt was made to connect a third-party account that was already
  connected to a different account, no error was communicated to the frontend. Fixed.

- When the headless provider signup endpoint was called while that flow was not pending,
  a crash would occur. This has been fixed to return a 409 (conflict).

- Microsoft provider: the URLs pointing to the login and graph API are now
  configurable via the app settings.


0.63.1 (2024-05-17)
*******************

Note worthy changes
-------------------

- When only ``allauth.account`` was installed, you could run into an exception
  stating "allauth.socialaccount not installed, yet its models are
  imported.". This has been fixed.

- When ``SOCIALACCOUNT_EMAIL_AUTHENTICATION`` was turned on, and a user would
  connect a third-party account for which email authentication would kick in,
  the connect was implicitly skipped. Fixed.

- The recommendation from the documentation to protect the Django admin login
  could cause an infinite redirect loop in case of
  ``AUTHENTICATED_LOGIN_REDIRECTS``. A decorator ``secure_admin_login()`` is now
  offered out of the box to ensure that the Django admin is properly secured by
  allauth (e.g. rate limits, 2FA).

- Subpackages from the ``tests`` package were packaged, fixed.


0.63.0 (2024-05-14)
*******************

Note worthy changes
-------------------

- New providers: TikTok, Lichess.

- Starting since version 0.62.0, new email addresses are always stored as lower
  case. In this version, we take the final step and also convert existing data
  to lower case, alter the database indices and perform lookups
  accordingly. Migrations are in place.  For rationale, see the note about email
  case sensitivity in the documentation.

- An official API for single-page and mobile application support is now
  available, via the new ``allauth.headless`` app.

- Added support for a honeypot field on the signup form. Real users do not see
  the field and therefore leave it empty. When bots do fill out the field
  account creation is silently skipped.


0.62.1 (2024-04-24)
*******************

- The ``tests`` package was accidentally packaged, fixed.


0.62.0 (2024-04-22)
*******************

Note worthy changes
-------------------

- Added a dummy provider, useful for testing purposes: ``allauth.socialaccount.providers.dummy``.

- Added a new provider, Atlassian

- Next URL handling been streamlined to be consistently applied. Previously, the
  password reset, change and email confirmation views only supported the
  ``success_url`` class-level property.

- Added support for logging in by email using a special code, also known as
  "Magic Code Login"

- Email addresses are now always stored as lower case. For rationale, see the
  note about email case sensitivity in the documentation.

- You can now alter the ``state`` parameter that is typically passed to the
  provider by overriding the new ``generate_state_param()`` adapter method.

- The URLs were not "hackable". For example, while ``/accounts/login/`` is valid
  ``/accounts/`` was not. Similarly, ``/accounts/social/connections/`` was
  valid, but ``/accounts/social/`` resulted in a 404. This has been
  addressed. Now, ``/accounts/`` redirects to the login or email management
  page, depending on whether or not the user is authenticated.  All
  ``/accounts/social/*`` URLs are now below ``/accounts/3rdparty/*``, where
  ``/accounts/social/connections`` is moved to the top-level
  ``/accounts/3rdparty/``.  The old endpoints still work as redirects are in
  place.

- Added a new setting, ``SOCIALACCOUNT_ONLY``, which when set to ``True``,
  disables all functionality with respect to local accounts.

- The OAuth2 handshake was not working properly in case of
  ``SESSION_COOKIE_SAMESITE = "Strict"``, fixed.

- Facebook: the default Graph API version is now v19.0.


Backwards incompatible changes
------------------------------

- The django-allauth required dependencies are now more fine grained.  If you do
  not use any of the social account functionality, a ``pip install
  django-allauth`` will, e.g., no longer pull in dependencies for handling
  JWT. If you are using social account functionality, install using ``pip install
  "django-allauth[socialaccount]"``.  That will install the dependencies covering
  most common providers. If you are using the Steam provider, install using ``pip
  install django-allauth[socialaccount,steam]``.


0.61.1 (2024-02-09)
*******************

Fixes
-----

- Fixed a ``RuntimeWarning`` that could occur when running inside an async
  environment (``'SyncToAsync' was never awaited``).


Security notice
---------------

- As part of the Google OAuth handshake, an ID token is obtained by direct
  machine to machine communication between the server running django-allauth and
  Google. Because of this direct communication, we are allowed to skip checking
  the token signature according to the `OpenID Connect Core 1.0 specification
  <https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation>`_.
  However, as django-allauth is used and built upon by third parties, this is an
  implementation detail with security implications that is easily overlooked. To
  mitigate potential issues, verifying the signature is now only skipped if it
  was django-allauth that actually fetched the access token.


0.61.0 (2024-02-07)
*******************

Note worthy changes
-------------------

- Added support for account related security notifications. When
  ``ACCOUNT_EMAIL_NOTIFICATIONS = True``, email notifications such as "Your
  password was changed", including information on user agent / IP address from where the change
  originated, will be emailed.

- Google: Starting from 0.52.0, the ``id_token`` is being used for extracting
  user information.  To accommodate for scenario's where django-allauth is used
  in contexts where the ``id_token`` is not posted, the provider now looks up
  the required information from the ``/userinfo`` endpoint based on the access
  token if the ``id_token`` is absent.


Security notice
---------------

- MFA: It was possible to reuse a valid TOTP code within its time window. This
  has now been addressed. As a result, a user can now only login once per 30
  seconds (``MFA_TOTP_PERIOD``).


Backwards incompatible changes
------------------------------

- The rate limit mechanism has received an update. Previously, when specifying
  e.g. ``"5/m"`` it was handled implicitly whether or not that limit was per IP,
  per user, or per action specific key. This has now been made explicit:
  ``"5/m/user"`` vs ``"5/m/ip"`` vs ``"5/m/key"``. Combinations are also supported
  now: ``"20/m/ip,5/m/key"`` . Additionally, the rate limit mechanism is now used
  throughout, including email confirmation cooldown as well as limitting failed login
  attempts.  Therefore, the ``ACCOUNT_LOGIN_ATTEMPTS_LIMIT`` and
  ``ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN`` settings are deprecated.
  See :doc:`Rate Limits <../account/rate_limits>` for details.


0.60.1 (2024-01-15)
*******************

Fixes
-----

- User sessions: after changing your password in case of ``ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False``, the list of
  sessions woud be empty instead of showing your current session.

- SAML: accessing the SLS/ACS views using a GET request would result in a crash (500).

- SAML: the login view did not obey the ``SOCIALACCOUNT_LOGIN_ON_GET = False`` setting.


Backwards incompatible changes
------------------------------

- Formally, email addresses are case sensitive because the local part (the part
  before the "@") can be a case sensitive user name.  To deal with this,
  workarounds have been in place for a long time that store email addresses in
  their original case, while performing lookups in a case insensitive
  style. This approach led to subtle bugs in upstream code, and also comes at a
  performance cost (``__iexact`` lookups). The latter requires case insensitive
  index support, which not all databases support. Re-evaluating the approach in
  current times has led to the conclusion that the benefits do not outweigh the
  costs.  Therefore, email addresses are now always stored as lower case, and
  migrations are in place to address existing records.



0.60.0 (2024-01-05)
*******************

Note worthy changes
-------------------

- Google One Tap Sign-In is now supported.

- You can now more easily change the URL to redirect to after a successful password
  change/set via the newly introduced ``get_password_change_redirect_url()``
  adapter method.

- You can now configure the primary key of all models by configuring
  ``ALLAUTH_DEFAULT_AUTO_FIELD``, for example to:
  ``"hashid_field.HashidAutoField"``.


Backwards incompatible changes
------------------------------

- You can now specify the URL path prefix that is used for all OpenID Connect
  providers using ``SOCIALACCOUNT_OPENID_CONNECT_URL_PREFIX``. By default, it is
  set to ``"oidc"``, meaning, an OpenID Connect provider with provider ID
  ``foo`` uses ``/accounts/oidc/foo/login/`` as its login URL. Set it to empty
  (``""``) to keep the previous URL structure (``/accounts/foo/login/``).

- The SAML default attribute mapping for ``uid`` has been changed to only
  include ``urn:oasis:names:tc:SAML:attribute:subject-id``. If the SAML response
  does not contain that, it will fallback to use ``NameID``.
