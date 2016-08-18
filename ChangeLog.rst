0.27.0 (2016-08-18)
*******************

Note worthy changes
-------------------

- Django 1.10 compatibility.

- The Twitter and GitHub providers now support querying of the email address.


Backwards incompatible changes
------------------------------

- When ``ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE`` was turned on, the e-mail field key
  changed from ``email`` to ``email1``, which could introduce subtle bugs. This
  has now been changed: there always is an ``email`` field, and optionally an
  ``email2`` field.

- The "You must type the same password each time" form validation error that can
  be triggered during signup is now added to the ``password2`` field instead of
  being added to the non field errors.

- The ``email_confirmation_sent`` signal is now passed ``request``,
  ``confirmation`` and ``signup`` instead of only the ``confirmation``.

- ``ACCOUNT_PASSWORD_MIN_LENGTH`` was already deprecated, but is now completely
  ignored if ``AUTH_PASSWORD_VALIDATORS`` is not empty.


0.26.1 (2016-07-25)
*******************

Note worthy changes
-------------------

- Locale files wrongly packaged, fixed.

- Fixed bug (``KeyError``) when ``ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE`` was set to
  ``True``.


0.26.0 (2016-07-24)
*******************

Note worthy changes
-------------------

- New providers: Weixin, Battle.net, Asana, Eve Online, 23andMe, Slack

- Django's password validation mechanism (see ``AUTH_PASSWORD_VALIDATORS``) is now
  used to validate passwords.

- By default, email confirmations are no longer stored in the
  database. Instead, the email confirmation mail contains an HMAC
  based key identifying the email address to confirm. The verification
  lookup includes a fallback to the previous strategy so that there is
  no negative impact on pending verification emails.

- A new setting ``ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE`` was added, requiring users to
  input their email address twice. The setting
  ``ACCOUNT_SIGNUP_PASSWORD_VERIFICATION`` has been renamed to
  ``ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE``.

- New translations: Latvian, Kyrgyz.


Backwards incompatible changes
------------------------------

- Dropped support for Django 1.6

- In order to accomodate for Django's password validation, the
  ``clean_password`` method of the adapter now takes an (optional)
  ``user`` parameter as its second argument.

- The new HMAC based keys may contain colons. If you have forked
  ``account/urls.py``, be sure to sync the ``account_confirm_email``
  pattern.


0.25.2 (2016-03-13)
*******************

Note worthy changes
-------------------

- Bug fix release (MemcachedKeyCharacterError: "Control characters not allowed")


0.25.1 (2016-03-13)
*******************

Note worthy changes
-------------------

- Bug fix release (AttributeError in password reset view).


0.25.0 (2016-03-12)
*******************

Note worthy changes
-------------------

- Many providers were added: Reddit, Untappd, GitLab, Stripe,
  Pinterest, Shopify, Draugiem, DigitalOcean, Robinhood,
  Bitbucket(OAuth2).

- The account connections view is now AJAX aware.

- You can now customize the template extension that is being used to
  render all HTML templates (``ACCOUNT_TEMPLATE_EXTENSION``)

- In order to be secure by default, users are now blocked from logging
  in after exceeding a maximum number of failed login attempts (see
  ``ACCOUNT_LOGIN_ATTEMPTS_LIMIT``,
  ``ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT``). Set
  ``ACCOUNT_LOGIN_ATTEMPTS_LIMIT`` to ``None`` to disable this
  functionality. Important: while this protects the allauth login view, it
  does not protect Django's admin login from being brute forced.

- New translations: Arabic, Lithuanian


Backwards incompatible changes
------------------------------

None


0.24.1 (2015-11-09)
*******************

Note worthy changes
-------------------

- Non-test code accidentally had test packages as a dependency.


Backwards incompatible changes
------------------------------

- Setting a password after logging in with a social account no longer logs out
  the user by default on Django 1.7+. Setting an initial password and changing
  the password both respect ``settings.ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE``.


0.24.0 (2015-11-08)
*******************

Note worthy changes
-------------------

- Django 1.9b1 compatibility.

- Seppo Erviälä contributed a Finnish translation, thanks!

- Iurii Kriachko contributed a Basecamp provider, thanks!

Backwards incompatible changes
------------------------------

- Increased ``SocialApp`` key/secret/token sizes to 191, decreased
  ``SocialAccount.uid`` size to 191. The latter was done in order to
  accomodate for MySQL in combination with utf8mb4 and contraints on
  ``uid``. Note that ``uid`` is used to store OpenID URLs, which can
  theoretically be longer than 191 characters, although in practice
  this does not seem to be the case. In case you really need to
  control the ``uid`` length, set ``settings.SOCIALACCOUNT_UID_MAX_LENGTH``
  accordingly. Migrations are in place.


0.23.0 (2015-08-02)
*******************

Note worthy changes
-------------------

- David Friedman contributed Edmodo support, thanks!

- Added support for ``ACCOUNT_LOGIN_ON_PASSWORD_RESET`` (thanks Julen!)


Backwards incompatible changes
------------------------------

None


0.22.0 (2015-07-23)
*******************

Note worthy changes
-------------------

- Reversal of the email confirmation url can now be overridden in
  the adapter (``get_email_confirmation_url``). Additionally, the
  complete confirmation email handling can be overridden via
  ``send_confirmation_mail``.

- Template context processors are no longer used.

- The Facebook Graph API fields (/me/?fields=...) can now be
  configured using the provider ``FIELDS`` setting.


Backwards incompatible changes
------------------------------

- Dropped support for Python 2.6 and Django <1.6.

- The default Facebook Graph API version is now v2.4.

- Template context processors are no longer used. The context
  processor for ``allauth.account`` was already empty, and the context
  processor for ``allauth.socialaccount`` has been converted into the
  :doc:``{% get_providers %} <templates>`` template tag.


0.21.0 (2015-07-02)
*******************

Note worthy changes
-------------------

- You can now tweak the authentication params per OAuth provider,
  as you already could for OAuth2. Contributed by Peter Rowlands,
  thanks.

- Nattaphoom Ch. contributed a Thai translation, thanks!

- Guoyu Hao contributed a Baidu provider, thanks!

- Rod Xavier Bondoc contributed support logging out on password
  change (see setting: ``ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE``)


Backwards incompatible changes
------------------------------

- In version 0.20.0 an ``account`` migration (``0002_email_max_length``)
  was added to alter the maximum length of the email
  field. Unfortunately, a side effect of this migration was that the
  ``unique=True`` setting slipped through as well. Hardcoding this to
  ``True`` is wrong, as uniqueness actually depends on the
  ``ACCOUNT_UNIQUE_EMAIL`` setting. We cannot create a followup ``0003``
  migration to set things straight, as the ``0002`` migration may fail
  on installations where email addresses are not unique. Therefore, we
  had to resort to changing an existing migration which is normally
  not the right thing to do. In case your installation has
  ``ACCOUNT_UNIQUE_EMAIL`` set to ``True``, you need not take any further
  action. In case it is set to ``False`` and migration ``0002`` already
  ran, please issue a ``--fake`` migration down to ``0001``, followed by a
  re-run of the updated ``0002``.


0.20.0 (2015-05-25)
*******************

Note worthy changes
-------------------

- Patrick Paul contributed a provider for Evernote, thanks!

- Josh Wright contributed a provider for Spotify, thanks!

- Björn Andersson added support for Dropbox OAuth2, thanks!

- guoqiao contributed a provider for Douban, thanks!


Backwards incompatible changes
------------------------------

- Given that the ``max_length`` for the Django 1.8 ``EmailField`` has been
  bumped to 254, allauth is following up. Migrations (``account``) are
  in place.


0.19.1 (2015-02-05)
*******************

Note worthy changes
-------------------

- Fixed migrations when using South & Django 1.6.


0.19.0 (2015-01-04)
*******************

Note worthy changes
-------------------

- Basil Shubin contributed an Odnoklassniki provider, thanks!

- Facebook: If the JS SDK is not available, for example due to a
  browser plugin like Disconnect.me that blocks it, login falls back
  to the regular non JS handshake.

- ``is_safe_url`` can now be overriden

- Facebook: The Graph API version is now configurable via
  ``SOCIALACCOUNT_PROVIDERS``.

- A Firefox Accounts provider was added by Jannis Leidel, thanks!

- Josh Owen contributed Coinbase support, thanks!

- Tomas Babej contributed a Slovak translation, thanks!

- Moved existing migrations into ``south_migrations``

- "zbryikt" contributed a Taiwanese Chinese translation, thanks!

- Added support for custom password rules via ``clean_password``.


Backwards incompatible changes
------------------------------

- In the upcoming Django 1.8 it is no longer possible to hookup an
  unsaved ``User`` instance to a ``SocialAccount``. Therefore, if you are
  inspecting the ``sociallogin`` object, you should now use
  ``sociallogin.user`` instead of ``sociallogin.account.user``.

- When users logged in while ``User.is_active`` was ``False``, they were
  sent to ``/accounts/inactive/`` in case of a social login, and
  received a form validation error in case of a local login. This
  needless inconsistency has been removed. The validation error no
  longer appears and local logins are also redirected to
  ``/accounts/inactive/``.

- In case you were overriding the ``ResetPasswordForm``: the save method
  now takes ``request`` as its first argument.

- All existing migrations have been moved into ``south_migrations``
  packages, this in order not to conflict with Django's built-in
  support for migrations. South 1.0 automatically picks up this new
  location. Upgrade South if you are still dependent on these
  migrations.


0.18.0 (2014-08-12)
*******************

Note worthy changes
-------------------

- Storing social access tokens is now optional
  (``SOCIALACCOUNT_STORE_TOKENS``).

- ``nimiq`` contributed ORCID support, thanks.

- All forms are now pluggable via a new setting:
  ``(SOCIAL)ACCOUNT_FORMS``.

- James Thompson contributed Windows Live support, thanks!


Backwards incompatible changes
------------------------------

- SECURITY: The Persona provider now requires the ``AUDIENCE`` parameter
  to be explicitly configured, as required by the Persona
  specification for security reasons.

- The inline Javascript is removed from the ``fbconnect.html`` template,
  which allows for a more strict ``Content-Security-Policy``. If you
  were using the builtin ``fbconnect.html`` this change should go by
  unnoticed.


0.17.0 (2014-06-16)
*******************

Note worthy changes
-------------------

- ``sourenaraya`` contributed Mail.Ru support, thanks.

- account: Justin Michalicek contributed support to control
  session life time and age: ``ACCOUNT_SESSION_COOKIE_AGE`` and
  ``ACCOUNT_SESSION_REMEMBER``.

- Serafeim Papastefanos contributed an Ukrainian translation,
  thanks!

- ``kkarwows`` contributed AppConfig support, thanks.

- socialaccount: Added Xing provider.

- socialaccount: Marcin Skarbek contributed Hubic support, thanks!

- Volodymyr Yatsyk contributed an Ukrainian translation, thanks!

- ``joke2k`` contributed an Italian translation, thanks!

- socialaccount: All providers now support the ``VERIFIED_EMAIL``
  property have e-mail addresses forced to be interpreted as
  verified.


Backwards incompatible changes
------------------------------

None


0.16.1 (2014-03-12)
*******************

Note worthy changes
-------------------

- Facebook login via Javascript was broken if ``auth_type`` was not
  set to ``reauthenticate``, fixed.
- Support for hooking up a callback when ``FB.init()`` is ready
  (``allauth.facebook.onInit``)

Backwards incompatible changes
------------------------------

None


0.16.0 (2014-03-10)
*******************

Note worthy changes
-------------------

- Nariman Gharib contributed a Persian translation, thanks!

- The custom signup form ``save`` has been deprecated in favour of a
  ``def signup(request, user)`` method.

- Facebook reauthentication now uses an ``auth_nonce``.

- Added a new option ``ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION``, to
  indicate whether or not e-mail confirmation is to automatically
  log in.

- socialaccount: Added Bitbucket provider.

- Jack Shedd contributed Tumblr support, thanks!

- Romanos Tsouroplis contributed Foursquare support, thanks!

- "excessivedemon" contributed Flickr support, thanks!

- Luis Diego García contributed Amazon and Paypal support, thanks!

- Stuart Ross contributed LinkedIn OAuth 2.0 support, thanks!


Backwards incompatible changes
------------------------------

- Previously, the ``save(user)`` was called on the custom signup form.
  However, this shadowed the existing ``save`` method in case a model
  form was used. To avoid confusion, the ``save`` method has been
  deprecated in favour of a ``def signup(request, user)`` method.

- The Amazon provider requires more space for ``token_secret``, so the
  maximum length restriction has been dropped. Migrations are in
  place.


0.15.0 (2013-12-01)
*******************

Note worthy changes
-------------------

- socialaccount: Added ``is_auto_signup_allowed`` to social account
  adapter.

- facebook: Added a new setting: VERIFIED_EMAIL.

- socialaccount: a collision on e-mail address when you sign up
  using a third party social account is now more clearly explained:
  "An account already exists with this e-mail address.  Please sign
  in to that account first, then connect your Google account".

- account: You are now automatically logged in after confirming
  your e-mail address during sign up.

- account: The ``/accounts/login/`` view now supports AJAX requests.

- facebook: The fbconnect.js script is now more pluggable.

- socialaccount: Markus Kaiserswerth contributed a Feedly
  provider, thanks!

- socialaccount: Dropped django-avatar support.

- openid: First, last and full name are now also queried together
  with the e-mail address. Thanks, @andrvb.

- openid: Compatibility fix for Django 1.6 (JSON serializer).

- account: Added support for ``ACCOUNT_CONFIRM_EMAIL_ON_GET``.


Backwards incompatible changes
------------------------------

- Instead of directly rendering and returning a template, logging in
  while the account is inactive or not yet confirmed now redirects to
  two new views: ``/accounts/inactive/`` respectively
  ``/accounts/confirm-email/``.

- The ``account/verification_sent.html`` template no longer receives the
  e-mail address in the context (``email``). Note that a message
  containing that e-mail address is still emitted using the messages
  framework.

- The ``/accounts/confirm_email/key/`` view has been
  renamed to ``/accounts/confirm-email/`` (human friendlier). Redirects
  are in place to handle old still pending confirmations.

- Built-in support for django-avatar has been removed. Offering such
  functionality means making choices which may not be valid for
  everyone. For example, allauth was downloading the image (which can
  take some time, or even block) in the context of the login, whereas
  a better place might be some celery background job. Additionally, in
  case of an error it simply ignored this. How about retries et al?
  Also, do you want to copy the avatar once at sign up, or do you want
  to update on each login? All in all, this functionality goes way
  beyond authentication and should be addressed elsewhere, beyond
  allauth scope. The original code has been preserved here so that you
  can easily reinstate it in your own project:
  https://gist.github.com/pennersr/7571752


0.14.2 (2013-11-16)
*******************

Note worthy changes
-------------------

- Compatibility fix for logging in with Django 1.6.

- Maksim Rukomoynikov contributed a Russian translation, thanks!


Backwards incompatible changes
------------------------------

- In case you were using the internal method
  ``generate_unique_username``, note that its signature has changed. It
  now takes a list of candidates to base the username on.


0.14.1 (2013-10-28)
*******************

Note worthy changes
-------------------

- PyPi did not render the README.rst properly.


Backwards incompatible changes
------------------------------

None


0.14.0 (2013-10-28)
*******************

Note worthy changes
-------------------

- Stuart Ross contributed AngelList support, thanks!

- LinkedIn: profile fields that are to be fetched are now
  configurable (``PROFILE_FIELDS`` provider-level setting).

- Udi Oron contributed a Hebrew translation, thanks!

- Add setting ``ACCOUNT_DEFAULT_HTTP_PROTOCOL`` (HTTPS support).

- George Whewell contributed Instagram support, thanks!

- Refactored adapter methods relating to creating and populating
  ``User`` instances.

- User creation methods in the ``Default(Social)AccountAdapter`` now
  have access to the ``request``.


Backwards incompatible changes
------------------------------

- The ``socialaccount/account_inactive.html`` template has been
  moved to ``account/account_inactive.html``.

- The adapter API for creating and populating users has been
  overhauled. As a result, the ``populate_new_user`` adapter methods
  have disappeared. Please refer to the section on "Creating and
  Populating User Instances" for more information.


0.13.0 (2013-08-31)
*******************

Note worthy changes
-------------------

- Koichi Harakawa contributed a Japanese translation, thanks!

- Added ``is_open_for_signup`` to DefaultSocialAccountAdapter.

- Added VK provider support.

- Marcin Spoczynski contributed a Polish translation, thanks!

- All views are now class-based.

- ``django.contrib.messages`` is now optional.

- "jresins" contributed a simplified Chinese, thanks!


Backwards incompatible changes
------------------------------

- The password reset from key success response now redirects to a
  "done" view (``/accounts/password/reset/key/done/``). This view has
  its own ``account/password_reset_from_key_done.html`` template. In
  previous versions, the success template was intertwined with the
  ``account/password_reset_from_key.html`` template.


0.12.0 (2013-07-01)
*******************

Note worthy changes
-------------------

- Added support for re-authenticated (forced prompt) by means of a
  new ``action="reauthenticate"`` parameter to the ``{%
  provider_login_url %}``

- Roberto Novaes contributed a Brazilian Portuguese translation,
  thanks!

- Daniel Eriksson contributed a Swedish translation, thanks!

- You can now logout from both allauth and Facebook via a
  Javascript helper: ``window.allauth.facebook.logout()``.

- Connecting a social account is now a flow that needs to be
  explicitly triggered, by means of a ``process="connect"`` parameter
  that can be passed along to the ``{% provider_login_url %}``, or a
  ``process=connect`` GET parameter.

- Tomas Marcik contributed a Czech translation, thanks!


Backwards incompatible changes
------------------------------

- The ``{% provider_login_url %}`` tag now takes an optional process
  parameter that indicates how to process the social login. As a
  result, if you include the template
  ``socialaccount/snippets/provider_list.html`` from your own overriden
  ``socialaccount/connections.html`` template, you now need to pass
  along the process parameter as follows:
  ``{% include "socialaccount/snippets/provider_list.html" with process="connect" %}``.

- Instead of inlining the required Facebook SDK Javascript wrapper
  code into the HTML, it now resides into its own .js file (served
  with ``{% static %}``). If you were using the builtin ``fbconnect.html``
  this change should go by unnoticed.


0.11.1 (2013-06-04)
*******************

Note worthy changes
-------------------

- Released (due to issue in disconnecting social accounts).

Backwards incompatible changes
------------------------------

None


0.11.0 (2013-06-02)
*******************

Note worthy changes
-------------------

- Moved logic whether or not a social account can be disconnected
  to the ``SocialAccountAdapter`` (``validate_disconnect``).

- Added ``social_account_removed`` signal.

- Implemented CSRF protection
  (http://tools.ietf.org/html/draft-ietf-oauth-v2-30#section-10.12).

- The ``user_logged_in`` signal now optionally receives a
  ``sociallogin`` parameter, in case of a social login.

- Added ``social_account_added`` (contributed by orblivion, thanks).

- Hatem Nassrat contributed Bitly support, thanks!

- Bojan Mihelac contributed a Croatian translation, thanks!

- Messages (as in ``django.contrib.messages``) are now configurable
  through templates.
- Added support for differentiating e-mail handling (verification,
  required) between local and social accounts:
  ``SOCIALACCOUNT_EMAIL_REQUIRED`` and
  ``SOCIALACCOUNT_EMAIL_VERIFICATION``.


Backwards incompatible changes
------------------------------

None


0.10.1 (2013-04-16)
*******************

Note worthy changes
-------------------

- Cleaning of ``username`` can now be overriden via
  ``DefaultAccountAdapter.clean_username``

- Fixed potential error (``assert``) when connecting social
  accounts.

- Added support for custom username handling in case of custom
  user models (``ACCOUNT_USER_MODEL_USERNAME_FIELD``).


Backwards incompatible changes
------------------------------

None


0.10.0 (2013-04-12)
*******************

Note worthy changes
-------------------

- Chris Davis contributed Vimeo support, thanks!

- Added support for overriding the URL to return to after
  connecting a social account
  (``allauth.socialaccount.adapter.DefaultSocialAccountAdapter.get_connect_redirect_url``).

- Python 3 is now supported!

- Dropped dependency on (unmaintained?) oauth2 package, in favor
  of requests-oauthlib.

- account: E-mail confirmation mails generated at signup can now
  be differentiated from regular e-mail confirmation mails by
  placing e.g. a welcome message into the
  ``account/email/email_confirmation_signup*`` templates. Thanks to
  Sam Solomon for the patch.

- account: Moved User instance creation to adapter so that e.g.
  username generation can be influenced. Thanks to John Bazik for
  the patch.

- Robert Balfre contributed Dropbox support, thanks!

- socialaccount: Added support for Weibo.

- account: Added support for sending HTML e-mail. Add
  ``*_message.html`` templates and they will be automatically picked
  up.

- Added support for passing along extra parameters to the OAuth2
  authentication calls, such as ``access_type`` (Google) or
  ``auth_type`` (Facebook).
- Both the login and signup view now immediately redirect to the
  login redirect url in case the user was already authenticated.

- Added support for closing down signups in a pluggable fashion,
  making it easy to hookup your own invitation handling mechanism.

- Added support for passing along extra parameters to the
  ``FB.login`` API call.


Backwards incompatible changes
------------------------------

- Logout no longer happens on GET request. Refer to the ``LogoutView``
  documentation for more background information. Logging out on GET
  can be restored by the setting ``ACCOUNT_LOGOUT_ON_GET``. Furthermore,
  after logging out you are now redirected to
  ``ACCOUNT_LOGOUT_REDIRECT_URL`` instead of rendering the
  ``account/logout.html`` template.

- ``LOGIN_REDIRECT_URLNAME`` is now deprecated. Django 1.5 accepts both
  URL names and URLs for ``LOGIN_REDIRECT_URL``, so we do so as well.

- ``DefaultAccountAdapter.stash_email_verified`` is now named
  ``stash_verified_email``.

- Django 1.4.3 is now the minimal requirement.

- Dropped dependency on (unmaintained?) oauth2 package, in favor of
  requests-oauthlib. So you will need to update your (virtual)
  environment accordingly.

- We noticed a very rare bug that affects end users who add Google
  social login to existing accounts. The symptom is you end up with
  users who have multiple primary email addresses which conflicts
  with assumptions made by the code. In addition to fixing the code
  that allowed duplicates to occur, there is a managegement command
  you can run if you think this effects you (and if it doesn't effect
  you there is no harm in running it anyways if you are unsure):

  - ``python manage.py account_unsetmultipleprimaryemails``

    - Will silently remove primary flags for email addresses that
      aren't the same as ``user.email``.

    - If no primary ``EmailAddress`` is ``user.email`` it will pick one
      at random and print a warning.

- The expiry time, if any, is now stored in a new column
  ``SocialToken.expires_at``. Migrations are in place.

- Furthermore, Facebook started returning longer tokens, so the
  maximum token length was increased. Again, migrations are in place.

- Login and signup views have been turned into class-based views.

- The template variable ``facebook_perms`` is no longer passed to the
  "facebook/fbconnect.html" template. Instead, ``fb_login_options``
  containing all options is passed.


0.9.0 (2013-01-30)
******************

Note worthy changes
-------------------

- account: ``user_signed_up`` signal now emits an optional
  ``sociallogin`` parameter so that receivers can easily differentiate
  between local and social signups.

- account: Added ``email_removed`` signal.

- socialaccount: Populating of User model fields is now
  centralized in the adapter, splitting up ``name`` into ``first_name``
  and ``last_name`` if these were not individually available.

- Ahmet Emre Aladağ contributed a Turkish translation, thanks!

- socialaccount: Added SocialAccountAdapter hook to allow for
  intervention in social logins.

- google: support for Google's ``verified_email`` flag to determine
  whether or not to send confirmation e-mails.

- Fábio Santos contributed a Portugese translation, thanks!

- socialaccount: Added support for Stack Exchange.

- socialaccount: Added ``get_social_accounts`` template tag.

- account: Default URL to redirect to after login can now be
  overriden via the adapter, both for login and e-mail confirmation
  redirects.


Backwards incompatible changes
------------------------------

- ``requests`` is now a dependency (dropped ``httplib2``).

- Added a new column ``SocialApp.client_id``. The value of ``key`` needs
  to be moved to the new ``client_id`` column. The ``key`` column is
  required for Stack Exchange. Migrations are in place to handle all
  of this automatically.


0.8.3 (2012-12-06)
******************

Note worthy changes
-------------------

- Markus Thielen contributed a German translation, thanks!

- The ``site`` foreign key from ``SocialApp`` to ``Site`` has been replaced
  by a ``ManyToManyField``. Many apps can be used across multiple domains
  (Facebook cannot).

- account: Added adapter class for increased pluggability. Added
  hook for 3rd party invitation system to by pass e-mail
  verification (``stash_email_verified``). Moved sending of mail to
  adapter.

- account: Added option to completely disable e-mail verification
  during signup.


Backwards incompatible changes
------------------------------

- The ``ACCOUNT_EMAIL_VERIFICATION`` setting is no longer a boolean
  based setting. Use a string value of "none", "optional" or
  "mandatory" instead.

- The template "account/password_reset_key_message.txt" has been moved
  to "account/email/password_reset_key_message.txt". The subject of
  the message has been moved into a template
  ("account/email/password_reset_key_subject.txt").

- The ``site`` foreign key from ``SocialApp`` to ``Site`` has been replaced
  by a ``ManyToManyField``. Many apps can be used across multiple
  domains (Facebook cannot).


0.8.2 (2012-10-10)
******************

Note worthy changes
-------------------

- Twitter: Login was broken due to change at in URLs at Twitter,
  fixed.

- LinkedIn: Added support for passing along the OAuth scope.

- account: Improved e-mail confirmation error handling, no more
  confusing 404s.

- account: Aldiantoro Nugroho contributed support for a new
  setting: ACCOUNT_USERNAME_MIN_LENGTH

- socialaccount: Added preliminary support for Mozilla Persona.

- account: Sam Solomon added various signals for email and
  password related changes.

- account: Usernames may now contain @, +, . and - characters.


Backwards incompatible changes
------------------------------

- Dropped support for ``CONTACT_EMAIL`` from the ``account`` template
  context processor. It was never documented and only used in the
  templates as an example -- there is no need to pollute the ``allauth``
  settings with that. If your templates rely on it then you will have
  to put it in a context processor yourself.


0.8.1 (2012-09-03)
******************

Note worthy changes
-------------------

- Python 2.6.2 compatibility issue, fixed.

- The example project was unintentionally packaged, fixed.


Backwards incompatible changes
------------------------------

None


0.8.0 (2012-09-01)
******************

Note worthy changes
-------------------

- account: Dropped dependency on the emailconfirmation app,
  integrating its functionality into the account app. This change is
  of major impact, please refer to the documentation on how to
  upgrade.

- account: Documented ACCOUNT_USERNAME_REQUIRED. This is actually
  not a new setting, but it somehow got overlooked in the
  documentation.

- account/socialaccount: Dropped the _tags postfix from the
  template tag libraries. Simply use {% load account %} and {% load
  socialaccount %}.

- Added signup and social login signals.

- SoundCloud: Rabi Alam contributed a SoundCloud provider, thanks!

- account: Sam Solomon cleaned up the e-mail management view:
  added proper redirect after POSTs, prevent deletion of primary
  e-mail. Thanks.

- account: When signing up, instead of generating a completely
  random username a more sensible username is automatically derived
  from first/last name or e-mail.


Backwards incompatible changes
------------------------------

- ``allauth`` now depends on Django 1.4 or higher.

- Major impact: dropped dependency on the ``emailconfirmation`` app, as
  this project is clearly left unmaintained. Important tickets such
  as https://github.com/pinax/django-email-confirmation/pull/5 are not
  being addressed. All models and related functionality have been
  directly integrated into the ``allauth.account`` app. When upgrading
  take care of the following:

  - The ``emailconfirmation`` setting ``EMAIL_CONFIRMATION_DAYS`` has been
    replaced by ``ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS``.

  - Instead of directly confirming the e-mail address upon the GET
    request the confirmation is now processed as part of an explicit
    POST. Therefore, a new template ``account/email_confirm.html`` must
    be setup.

  - Existing ``emailconfirmation`` data should be migrated to the new
    tables. For this purpose a special management command is
    available: ``python manage.py
    account_emailconfirmationmigration``. This command does not drop
    the old ``emailconfirmation`` tables -- you will have to do this
    manually yourself. Why not use South? EmailAddress uniqueness
    depends on the configuration (``ACCOUNT_UNIQUE_EMAIL``), South does
    not handle settings dependent database models.

- ``{% load account_tags %}`` is deprecated, simply use: ``{% load account %}``

- ``{% load socialaccount_tags %}`` is deprecated, simply use:
  ``{% load socialaccount %}``


0.7.0 (2012-07-18)
******************

Note worthy changes
-------------------

- Facebook: Facundo Gaich contributed support for dynamically
  deriving the Facebook locale from the Django locale, thanks!.

- OAuth: All OAuth/OAuth2 tokens are now consistently stored
  across the board. Cleaned up OAuth flow removing superfluous
  redirect.

- Facebook: Dropped Facebook SDK dependency.

- socialaccount: DRY focused refactoring of social login.

- socialaccount: Added support for Google OAuth2 and Facebook
  OAuth2. Fixed GitHub.

- account: Added verified_email_required decorator.

- socialaccount: When signing up, user.first/last_name where
  always taken from the provider signup data, even when a custom
  signup form was in place that offered user inputs for editting
  these fields. Fixed.


Backwards incompatible changes
------------------------------

None


0.6.0 (2012-06-20)
******************

Note worthy changes
-------------------

- account: Added ACCOUNT_USER_DISPLAY to render a user name
  without making assumptions on how the user is represented.

- allauth, socialaccount: Removed the last remaining bits of
  hardcodedness with respect to the enabled social authentication
  providers.

- account: Added ACCOUNT_AUTHENTICATION_METHOD setting, supporting
  login by username, e-mail or both.


Backwards incompatible changes
------------------------------

- The ``ACCOUNT_EMAIL_AUTHENTICATION`` setting has been dropped in favor
  of ``ACCOUNT_AUTHENTICATION_METHOD``.

- The login form field is now always named ``login``. This used to by
  either ``username`` or ``email``, depending on the authentication
  method. If needed, update your templates accordingly.

- The ``allauth`` template tags (containing template tags for
  OpenID, Twitter and Facebook) have been removed. Use the
  ``socialaccount`` template tags instead (specifically: ``{% provider_login_url
  ... %}``).

- The ``allauth.context_processors.allauth`` context processor has been
  removed, in favor of
  ``allauth.socialaccount.context_processors.socialaccount``. In doing
  so, all hardcodedness with respect to providers (e.g
  ``allauth.facebook_enabled``) has been removed.


0.5.0 (2012-06-08)
******************

Note worthy changes
-------------------

- account: Added setting ACCOUNT_PASSWORD_MIN_LENGTH for
  specifying the minimum password length.

- socialaccount: Added generic OAuth2 support. Added GitHub
  support as proof of concept.

- socialaccount: More refactoring: generic provider & OAuth
  consumer approach. Added LinkedIn support to test this approach.

- socialaccount: Introduced generic models for storing social
  apps, accounts and tokens in a central and consistent manner,
  making way for adding support for more account providers. Note:
  there is more refactoring to be done -- this first step only
  focuses on the database models.

- account: E-mail confirmation mails are now automatically resent
  whenever a user attempts to login with an unverified e-mail
  address (if ACCOUNT_EMAIL_VERIFICATION=True).


Backwards incompatible changes
------------------------------

- Upgrade your ``settings.INSTALLED_APPS``: Replace ``allauth.<provider>``
  (where provider is one of ``twitter``, ``facebook`` or ``openid``) with
  ``allauth.socialaccount.providers.<provider>``

- All provider related models (``FacebookAccount``, ``FacebookApp``,
  ``TwitterAccount``, ``TwitterApp``, ``OpenIDAccount``) have been unified
  into generic ``SocialApp`` and ``SocialAccount`` models. South migrations
  are in place to move the data over to the new models, after which
  the original tables are dropped. Therefore, be sure to run migrate
  using South.


0.4.0 (2012-03-25)
******************

Note worthy changes
-------------------

- account: The render_value parameter of all PasswordInput fields
  used can now be configured via a setting.

- account: Added support for prefixing the subject of sent emails.

- account: Added support for a plugging in a custom signup form
  used for additional questions to ask during signup.

- account: ``is_active`` is no longer used to keep users with an
  unverified e-mail address from loging in.

- Dropping uniform dependency. Moved uniform templates into
  example project.


Backwards incompatible changes
------------------------------

None


0.3.0 (2012-01-19)
******************

Note worthy changes
-------------------

- The e-mail authentication backend now attempts to use the
  'username' parameter as an e-mail address. This is needed to
  properly integrate with other apps invoking authenticate.

- SmileyChris contributed support for automatically generating a
  user name at signup when ``ACCOUNT_USERNAME_REQUIRED`` is set to
  False.

- Vuong Nguyen contributed support for (optionally) asking for the
  password just once during signup
  (``ACCOUNT_SIGNUP_PASSWORD_VERIFICATION``).

- The Twitter oauth sequence now respects the "oauth_callback"
  parameter instead of defaulting to the callback URL
  configured at Twitter.

- Pass along ``?next=`` parameter between login and signup views.

- Added Dutch translation.

- Added template tags for pointing to social login URLs. These
  tags automatically pass along any ``?next=``
  parameter. Additionally, added an overall allauth_tags that
  gracefully degrades when e.g. allauth.facebook is not installed.

- Pass along next URL, if any, at ``/accounts/social/signup/``.

- Duplicate email address handling could throw a
  MultipleObjectsReturned exception, fixed.

- Removed separate social account login view, in favour of having
  a single unified login view including both forms of login.

- Added support for passing along a next URL parameter to
  Facebook, OpenID logins.

- Added support for django-avatar, copying the Twitter profile
  image locally on signup.

- ``allauth/account/forms.py`` (``BaseSignupForm.clean_email``): With
  ``ACCOUNT_EMAIL_REQUIRED=False``, empty email addresses were
  considered duplicates. Fixed.

- The existing migrations for allauth.openid were not compatible
  with MySQL due to the use of an URLField with max_length above
  255. The issue has now been addressed but unfortunately at the
  cost of the existing migrations for this app. Existing
  installations will have to be dealt with manually (altering the
  "identity" column of OpenIDAccount, deleting ghost migrations).

Backwards incompatible changes
------------------------------

- None
