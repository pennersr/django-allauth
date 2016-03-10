## (Unreleased)

* Several providers were added: thanks to Wendy Edwards for Reddit
support, Luke Crouch for Untappd support, Daniel Widerin for
GitLab support, and Yaroslav Muravsky for Pinterest support.

## 0.24.1 (2015-11-09)

* Non-test code accidentally had test packages as a dependency.

## 0.24.0 (2015-11-08)
	
* Django 1.9b1 compatibility.
* Increased `SocialApp` key/secret/token sizes to 191, decreased
`SocialAccount.uid` size to 191. The latter was done in order to
accomodate for MySQL in combination with utf8mb4 and contraints on
`uid`. Note that `uid` is used to store OpenID URLs, which can
theoretically be longer than 191 characters, although in practice
this does not seem to be the case. In case you really need to
control the `uid` length, set
`settings.SOCIALACCOUNT_UID_MAX_LENGTH` accordingly.  
  Migrations are in place.
* Seppo Erviälä contributed a Finnish translation, thanks!
* Iurii Kriachko contributed a Basecamp provider, thanks!

## 0.23.0 (2015-08-02)

* David Friedman contributed Edmodo support, thanks!
* Added support for `ACCOUNT_LOGIN_ON_PASSWORD_RESET` (thanks Julen!)

## 0.22.0 (2015-07-23)

* Reversal of the email confirmation url can now be overridden in
the adapter (`get_email_confirmation_url`). Additionally, the
complete confirmation email handling can be overridden via
`send_confirmation_mail`.
* Dropped support for Python 2.6 and Django <1.6.
* Template context processors are no longer used.
* The Facebook Graph API fields (/me/?fields=...) can now be
configured using the provider `FIELDS` setting.
* The default Facebook Graph API version is now v2.4.

## 0.21.0 (2015-07-02)

* You can now tweak the authentication params per OAuth provider,
as you already could for OAuth2. Contributed by Peter Rowlands,
thanks.
* Nattaphoom Ch. contributed a Thai translation, thanks!
* Guoyu Hao contributed a Baidu provider, thanks!
* Rod Xavier Bondoc contributed support logging out on password
change (see setting: `ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE`)

## 0.20.0 (2015-05-25)

* Given that the `max_length` for the Django 1.8 `EmailField` has
been bumped to 254, allauth is following up. Migrations
(`account`) are in place.
* Patrick Paul contributed a provider for Evernote, thanks!
* Josh Wright contributed a provider for Spotify, thanks!
* Björn Andersson added support for Dropbox OAuth2, thanks!
* guoqiao contributed a provider for Douban, thanks!

## 0.19.1 (2015-02-05)

* Fixed migrations when using South & Django 1.6.

## 0.19.0 (2015-01-04)

* Basil Shubin contributed an Odnoklassniki provider, thanks!
* Facebook: If the JS SDK is not available, for example due to a
browser plugin like Disconnect.me that blocks it, login falls back
to the regular non JS handshake.
* `is_safe_url` can now be overriden
* Facebook: The Graph API version is now configurable via
`SOCIALACCOUNT_PROVIDERS`.
* A Firefox Accounts provider was added by Jannis Leidel, thanks!
* Josh Owen contributed Coinbase support, thanks!
* Tomas Babej contributed a Slovak translation, thanks!
* Moved existing migrations into `south_migrations`
* "zbryikt" contributed a Taiwanese Chinese translation, thanks!
* Added support for custom password rules via `clean_password`.

## 0.18.0 (2014-08-12)


* SECURITY: the Persona provider now requires the `AUDIENCE`
parameter to be explicitly configured, as required by the Persona
specification for security reasons.
* Storing social access tokens is now optional
(`SOCIALACCOUNT_STORE_TOKENS`).
* Removed the inline Javascript from the `fbconnect.html`
template. This allows for a more strict `Content-Security-Policy`
(thanks to Andrean Franc).
* `nimiq` contributed ORCID support, thanks.
* All forms are now pluggable via a new setting:
`(SOCIAL)ACCOUNT_FORMS`.
* James Thompson contributed Windows Live support, thanks!

## 0.17.0 (2014-06-16)

* `sourenaraya` contributed Mail.Ru support, thanks.
* account: Justin Michalicek contributed support to control
session life time and age: `ACCOUNT_SESSION_COOKIE_AGE` and
`ACCOUNT_SESSION_REMEMBER`.
* Serafeim Papastefanos contributed an Ukrainian translation,
thanks!
* `kkarwows` contributed AppConfig support, thanks.
* socialaccount: Added Xing provider.
* socialaccount: Marcin Skarbek contributed Hubic support, thanks!
* Volodymyr Yatsyk contributed an Ukrainian translation, thanks!
* `joke2k` contributed an Italian translation, thanks!
* socialaccount: All providers now support the `VERIFIED_EMAIL`
property have e-mail addresses forced to be interpreted as
verified.

## 0.16.1 (2014-03-12)

* Facebook login via Javascript was broken if `auth_type` was not
set to `reauthenticate`, fixed.
* Support for hooking up a callback when `FB.init()` is ready
(`allauth.facebook.onInit`)

## 0.16.0 (2014-03-10)

* Nariman Gharib contributed a Persian translation, thanks!
* The custom signup form `save` has been deprecated in favour of a
`def signup(request, user)` method.
* Facebook reauthentication now uses an `auth_nonce`.
* Added a new option `ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION`, to
indicate whether or not e-mail confirmation is to automatically
log in.
* socialaccount: Added Bitbucket provider.
* Jack Shedd contributed Tumblr support, thanks!
* Romanos Tsouroplis contributed Foursquare support, thanks!
* "excessivedemon" contributed Flickr support, thanks!
* Luis Diego García contributed Amazon and Paypal support, thanks!
* Stuart Ross contributed LinkedIn OAuth 2.0 support, thanks!

## 0.15.0 (2013-12-01)

* socialaccount: Added `is_auto_signup_allowed` to social account
adapter.
* facebook: Added a new setting: VERIFIED_EMAIL.
    
* socialaccount: a collision on e-mail address when you sign up
using a third party social account is now more clearly explained:
"An account already exists with this e-mail address.  Please sign
in to that account first, then connect your Google account".
* account: You are now automatically logged in after confirming
your e-mail address during sign up.
* account: The `/accounts/login/` view now supports AJAX requests.
* account: Instead of directly rendering and returning a template,
logging in while the account is inactive or not yet confirmed now
redirects to two new views: `/accounts/inactive/` respectively
`/accounts/confirm-email/`.
* account: The `account/verification_sent.html` template no longer
receives the e-mail address in the context (`email`). Note that a
message containing that e-mail address is still emitted using the
messages framework.
* account: The `/accounts/confirm_email/key/` view has been
renamed to `/accounts/confirm-email/` (human
friendlier). Redirects are in place to handle old still pending
confirmations.
* facebook: The fbconnect.js script is now more pluggable.
* socialaccount: Markus Kaiserswerth contributed a Feedly
provider, thanks!
* socialaccount: Dropped django-avatar support.
* openid: First, last and full name are now also queried together
with the e-mail address. Thanks, @andrvb.
* openid: Compatibility fix for Django 1.6 (JSON serializer).
* account: Added support for `ACCOUNT_CONFIRM_EMAIL_ON_GET`.

## 0.14.2 (2013-11-16)

* Compatibility fix for logging in with Django 1.6.
* Maksim Rukomoynikov contributed a Russian translation, thanks!

## 0.14.1 (2013-10-28)

* PyPi did not render the README.rst properly.

## 0.14.0 (2013-10-28)

* Stuart Ross contributed AngelList support, thanks!
* LinkedIn: profile fields that are to be fetched are now
configurable (`PROFILE_FIELDS` provider-level setting).
* Udi Oron contributed a Hebrew translation, thanks!
* Add setting `ACCOUNT_DEFAULT_HTTP_PROTOCOL` (HTTPS support).
* George Whewell contributed Instagram support, thanks!
* Refactored adapter methods relating to creating and populating
`User` instances.
* User creation methods in the `Default(Social)AccountAdapter` now
have access to the `request`.

## 0.13.0 (2013-08-31)

* Koichi Harakawa contributed a Japanese translation, thanks!
* Added `is_open_for_signup` to DefaultSocialAccountAdapter.
* Added VK provider support.
* Marcin Spoczynski contributed a Polish translation, thanks!
* All views are now class-based.
* The password reset from key success response now redirects to a
"done" view (`/accounts/password/reset/key/done/`). This view has
its own `account/password_reset_from_key_done.html` template. In
previous versions, the success template was intertwined with the
`account/password_reset_from_key.html` template.
* `django.contrib.messages` is now optional.
* "jresins" contributed a simplified Chinese, thanks!

## 0.12.0 (2013-07-01)

* Added support for re-authenticated (forced prompt) by means of a
new `action="reauthenticate"` parameter to the `{%
provider_login_url %}`
* Roberto Novaes contributed a Brazilian Portuguese translation,
thanks!
* Daniel Eriksson contributed a Swedish translation, thanks!
* You can now logout from both allauth and Facebook via a
Javascript helper: `window.allauth.facebook.logout()`.
* Connecting a social account is now a flow that needs to be
explicitly triggered, by means of a `process="connect"` parameter
that can be passed along to the `{% provider_login_url %}`, or a
`process=connect` GET parameter.
* Tomas Marcik contributed a Czech translation, thanks!

## 0.11.1 (2013-06-04)

* Released (due to issue in disconnecting social accounts).

## 0.11.0 (2013-06-02)

* Moved logic whether or not a social account can be disconnected
to the `SocialAccountAdapter` (`validate_disconnect`).
* Added `social_account_removed` signal.
* Implemented CSRF protection
(http://tools.ietf.org/html/draft-ietf-oauth-v2-30#section-10.12).
* The `user_logged_in` signal now optionally receives a
`sociallogin` parameter, in case of a social login.
* Added `social_account_added` (contributed by orblivion, thanks).
* Hatem Nassrat contributed Bitly support, thanks!
* Bojan Mihelac contributed a Croatian translation, thanks!
* Messages (as in `django.contrib.messages`) are now configurable
through templates.
* Added support for differentiating e-mail handling (verification,
required) between local and social accounts:
`SOCIALACCOUNT_EMAIL_REQUIRED` and
`SOCIALACCOUNT_EMAIL_VERIFICATION`.

## 0.10.1 (2013-04-16)

* Cleaning of `username` can now be overriden via
`DefaultAccountAdapter.clean_username`
* Fixed potential error (`assert`) when connecting social
accounts.
* Added support for custom username handling in case of custom
user models (`ACCOUNT_USER_MODEL_USERNAME_FIELD`).

## 0.10.0 (2013-04-12)

* Chris Davis contributed Vimeo support, thanks!
* Added support for overriding the URL to return to after
connecting a social account
(`allauth.socialaccount.adapter.DefaultSocialAccountAdapter.get_connect_redirect_url`).
* Python 3 is now supported!
* Dropped dependency on (unmaintained?) oauth2 package, in favor
of requests-oauthlib.
* account: E-mail confirmation mails generated at signup can now
be differentiated from regular e-mail confirmation mails by
placing e.g. a welcome message into the
`account/email/email_confirmation_signup*` templates. Thanks to
Sam Solomon for the patch.
* account: Moved User instance creation to adapter so that e.g.
username generation can be influenced. Thanks to John Bazik for
the patch.
* Robert Balfre contributed Dropbox support, thanks!
* socialaccount: Added support for Weibo.
* account: Added support for sending HTML e-mail. Add
`*_message.html` templates and they will be automatically picked
up.
* socialaccount: The refresh token and token expiry time, if any,
are now stored in `SocialToken`.
* Added support for passing along extra parameters to the OAuth2
authentication calls, such as `access_type` (Google) or
`auth_type` (Facebook).
* Both the login and signup view now immediately redirect to the
login redirect url in case the user was already authenticated.
* Added support for closing down signups in a pluggable fashion,
making it easy to hookup your own invitation handling mechanism.
* Added support for passing along extra parameters to the
`FB.login` API call.

## 0.9.0 (2013-01-30)

* account: `user_signed_up` signal now emits an optional
`sociallogin` parameter so that receivers can easily differentiate
between local and social signups.
* account: Added `email_removed` signal.
* socialaccount: Populating of User model fields is now
centralized in the adapter, splitting up `name` into `first_name`
and `last_name` if these were not individually available.
* Ahmet Emre Aladağ contributed a Turkish translation, thanks!
* socialaccount: Added SocialAccountAdapter hook to allow for
intervention in social logins.
* google: support for Google's `verified_email` flag to determine
whether or not to send confirmation e-mails.
* Fábio Santos contributed a Portugese translation, thanks!
* socialaccount: Added support for Stack Exchange.
* socialaccount: Added `get_social_accounts` template tag.
* account: Default URL to redirect to after login can now be
overriden via the adapter, both for login and e-mail confirmation
redirects.

## 0.8.3 (2012-12-06)

* Markus Thielen contributed a German translation, thanks!
* The `site` foreign key from `SocialApp` to `Site` has been
replaced by a `ManyToManyField`. Many apps can be used across
multiple domains (Facebook cannot).
* account: Added adapter class for increased pluggability. Added
hook for 3rd party invitation system to by pass e-mail
verification (`stash_email_verified`). Moved sending of mail to
adapter.
* account: Added option to completely disable e-mail verification
during signup.

## 0.8.2 (2012-10-10)

* Twitter: Login was broken due to change at in URLs at Twitter,
fixed.
* LinkedIn: Added support for passing along the OAuth scope.
* account: Improved e-mail confirmation error handling, no more
confusing 404s.
* account: Aldiantoro Nugroho contributed support for a new
setting: ACCOUNT_USERNAME_MIN_LENGTH
* socialaccount: Added preliminary support for Mozilla Persona.
* account: Sam Solomon added various signals for email and
password related changes.
* account: Usernames may now contain @, +, . and - characters.

## 0.8.1 (2012-09-03)

* Python 2.6.2 compatibility issue, fixed.
* The example project was unintentionally packaged, fixed.

## 0.8.0 (2012-09-01)

* account: Dropped dependency on the emailconfirmation app,
integrating its functionality into the account app. This change is
of major impact, please refer to the documentation on how to
upgrade.
* account: Documented ACCOUNT_USERNAME_REQUIRED. This is actually
not a new setting, but it somehow got overlooked in the
documentation.
* account/socialaccount: Dropped the _tags postfix from the
template tag libraries. Simply use {% load account %} and {% load
socialaccount %}.
* Added signup and social login signals.
* SoundCloud: Rabi Alam contributed a SoundCloud provider, thanks!
* account: Sam Solomon cleaned up the e-mail management view:
added proper redirect after POSTs, prevent deletion of primary
e-mail. Thanks.
* account: When signing up, instead of generating a completely
random username a more sensible username is automatically derived
from first/last name or e-mail.

## 0.7.0 (2012-07-18)

* Facebook: Facundo Gaich contributed support for dynamically
deriving the Facebook locale from the Django locale, thanks!.
* OAuth: All OAuth/OAuth2 tokens are now consistently stored
across the board. Cleaned up OAuth flow removing superfluous
redirect.
* Facebook: Dropped Facebook SDK dependency.
* socialaccount: DRY focused refactoring of social login.
* socialaccount: Added support for Google OAuth2 and Facebook
OAuth2. Fixed GitHub.
* account: Added verified_email_required decorator.
* socialaccount: When signing up, user.first/last_name where
always taken from the provider signup data, even when a custom
signup form was in place that offered user inputs for editting
these fields. Fixed.

## 0.6.0 (2012-06-20)

* account: Added ACCOUNT_USER_DISPLAY to render a user name
without making assumptions on how the user is represented.
* allauth, socialaccount: Removed the last remaining bits of
hardcodedness with respect to the enabled social authentication
providers.
* account: Added ACCOUNT_AUTHENTICATION_METHOD setting, supporting
login by username, e-mail or both.

## 0.5.0 (2012-06-08)

* account: Added setting ACCOUNT_PASSWORD_MIN_LENGTH for
specifying the minimum password length.
* socialaccount: Added generic OAuth2 support. Added GitHub
support as proof of concept.
* socialaccount: More refactoring: generic provider & OAuth
consumer approach. Added LinkedIn support to test this approach.
* socialaccount: Introduced generic models for storing social
apps, accounts and tokens in a central and consistent manner,
making way for adding support for more account providers. Note:
there is more refactoring to be done -- this first step only
focuses on the database models.
* account: E-mail confirmation mails are now automatically resent
whenever a user attempts to login with an unverified e-mail
address (if ACCOUNT_EMAIL_VERIFICATION=True).

## 0.4.0 (2012-03-25)

* account: The render_value parameter of all PasswordInput fields
used can now be configured via a setting.
* account: Added support for prefixing the subject of sent emails.
* account: Added support for a plugging in a custom signup form
used for additional questions to ask during signup.
* account: `is_active` is no longer used to keep users with an
unverified e-mail address from loging in.
* Dropping uniform dependency. Moved uniform templates into
example project.

## 0.3.0 (2012-01-19)

* The e-mail authentication backend now attempts to use the
'username' parameter as an e-mail address. This is needed to
properly integrate with other apps invoking authenticate.
* SmileyChris contributed support for automatically generating a
user name at signup when `ACCOUNT_USERNAME_REQUIRED` is set to
False.
* Vuong Nguyen contributed support for (optionally) asking for the
password just once during signup
(`ACCOUNT_SIGNUP_PASSWORD_VERIFICATION`).
* The Twitter oauth sequence now respects the "oauth_callback"
parameter instead of defaulting to the callback URL
configured at Twitter.
* Pass along `?next=` parameter between login and signup views.
* Added Dutch translation.
* Added template tags for pointing to social login URLs. These
tags automatically pass along any `?next=`
parameter. Additionally, added an overall allauth_tags that
gracefully degrades when e.g. allauth.facebook is not installed.
* Pass along next URL, if any, at `/accounts/social/signup/`.
* Duplicate email address handling could throw a
MultipleObjectsReturned exception, fixed.
* Removed separate social account login view, in favour of having
a single unified login view including both forms of login.
* Added support for passing along a next URL parameter to
Facebook, OpenID logins.
* Added support for django-avatar, copying the Twitter profile
image locally on signup.
* `allauth/account/forms.py` (`BaseSignupForm.clean_email`): With
`ACCOUNT_EMAIL_REQUIRED=False`, empty email addresses were
considered duplicates. Fixed.
* The existing migrations for allauth.openid were not compatible
with MySQL due to the use of an URLField with max_length above
255. The issue has now been addressed but unfortunately at the
cost of the existing migrations for this app. Existing
installations will have to be dealt with manually (altering the
"identity" column of OpenIDAccount, deleting ghost migrations).
