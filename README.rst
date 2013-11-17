==========================
Welcome to django-allauth!
==========================

.. image:: https://badge.fury.io/py/django-allauth.png
   :target: http://badge.fury.io/py/django-allauth

.. image:: https://travis-ci.org/pennersr/django-allauth.png
   :target: http://travis-ci.org/pennersr/django-allauth

.. image:: https://pypip.in/d/django-allauth/badge.png
   :target: https://crate.io/packages/django-allauth?version=latest

.. image:: https://coveralls.io/repos/pennersr/django-allauth/badge.png?branch=master
   :alt: Coverage Status
   :target: https://coveralls.io/r/pennersr/django-allauth

Integrated set of Django applications addressing authentication,
registration, account management as well as 3rd party (social) account
authentication.

Rationale
=========

Most existing Django apps that address the problem of social
authentication focus on just that. You typically need to integrate
another app in order to support authentication via a local
account.

This approach separates the worlds of local and social
authentication. However, there are common scenarios to be dealt with
in both worlds. For example, an e-mail address passed along by an
OpenID provider is not guaranteed to be verified. So, before hooking
an OpenID account up to a local account the e-mail address must be
verified. So, e-mail verification needs to be present in both worlds.

Integrating both worlds is quite a tedious process. It is definately
not a matter of simply adding one social authentication app, and one
local account registration app to your `INSTALLED_APPS` list.

This is the reason this project got started -- to offer a fully
integrated authentication app that allows for both local and social
authentication, with flows that just work.


Overview
========

Requirements
------------

- Python 2.6, 2.7 or 3.3

- Django (1.4.3+)

- python-openid or python3-openid (depending on your Python version)

- requests and requests-oauthlib

Supported Flows
---------------

- Signup of both local and social accounts

- Connecting more than one social account to a local account

- Disconnecting a social account -- requires setting a password if
  only the local account remains

- Optional instant-signup for social accounts -- no questions asked

- E-mail address management (multiple e-mail addresses, setting a primary)

- Password forgotten flow

- E-mail address verification flow

Supported Providers
-------------------

- AngelList (OAuth2)

- Bitly (OAuth2)

- Dropbox (OAuth)

- Facebook (both OAuth2 and JS SDK)

- Github

- Google (OAuth2)

- Instagram

- LinkedIn

- OpenId

- Persona

- SoundCloud (OAuth2)

- Stack Exchange (OAuth2)

- Twitch (OAuth2)

- Twitter

- Vimeo (OAuth)

- VK (OAuth2)

- Weibo (OAuth2)

Note: OAuth/OAuth2 support is built using a common code base, making it easy to add support for additional OAuth/OAuth2 providers. More will follow soon...


Features
--------

- Supports multiple authentication schemes (e.g. login by user name,
  or by e-mail), as well as multiple strategies for account
  verification (ranging from none to e-mail verification).

- All access tokens are consistently stored so that you can publish
  wall updates etc.

Architecture & Design
---------------------

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
------

settings.py::

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        "django.core.context_processors.request",
        ...
        "allauth.account.context_processors.account",
        "allauth.socialaccount.context_processors.socialaccount",
        ...
    )

    AUTHENTICATION_BACKENDS = (
        ...
        # Needed to login by username in Django admin, regardless of `allauth`
        "django.contrib.auth.backends.ModelBackend",

        # `allauth` specific authentication methods, such as login by e-mail
        "allauth.account.auth_backends.AuthenticationBackend",
        ...
    )

    INSTALLED_APPS = (
        ...
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        # ... include the providers you want to enable:
        'allauth.socialaccount.providers.angellist',
        'allauth.socialaccount.providers.bitly',
        'allauth.socialaccount.providers.dropbox',
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.github',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.instagram',
        'allauth.socialaccount.providers.linkedin',
        'allauth.socialaccount.providers.openid',
        'allauth.socialaccount.providers.persona',
        'allauth.socialaccount.providers.soundcloud',
        'allauth.socialaccount.providers.stackexchange',
        'allauth.socialaccount.providers.twitch',
        'allauth.socialaccount.providers.twitter',
        'allauth.socialaccount.providers.vimeo',
        'allauth.socialaccount.providers.vk',
        'allauth.socialaccount.providers.weibo',
        ...
    )

urls.py::

    urlpatterns = patterns('',
        ...
        (r'^accounts/', include('allauth.urls')),
        ...
    )


Post-Installation
-----------------

In your django root execute the command below to create your database tables::

    ./manage.py syncdb

Now start your server, visit your admin pages (http://localhost:8000/admin )
and follow these steps:

  1. Add a Site object for your domain
  2. For each provider you want, enter in Social App → Add Social App
  3. Choose the site, social provider and the credentials you obtained from the provider.


Configuration
-------------

Available settings:

ACCOUNT_ADAPTER (="allauth.account.adapter.DefaultAccountAdapter")
  Specifies the adapter class to use, allowing you to alter certain
  default behaviour.

ACCOUNT_AUTHENTICATION_METHOD (="username" | "email" | "username_email")
  Specifies the login method to use -- whether the user logs in by
  entering his username, e-mail address, or either one of both.

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
  the protocol is not enforced by any of the views. There are numerous
  third party packages available for enforcing `https`, use those.

ACCOUNT_LOGOUT_ON_GET (=False)
  Determines whether or not the user is automatically logged out by a
  mere GET request. See documentation for the `LogoutView` for
  details.

ACCOUNT_LOGOUT_REDIRECT_URL (="/")
  The URL (or URL name) to return to after the user logs out. This is
  the counterpart to Django's `LOGIN_REDIRECT_URL`.

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

SOCIALACCOUNT_PROVIDERS (= dict)
  Dictionary containing provider specific settings.


Upgrading
---------

From 0.14.1
***********

- In case you were using the internal method
  `generate_unique_username`, note that its signature has changed. It
  now takes a list of candidates to base the username on.

From 0.13.0
***********

- The `socialaccount/account_inactive.html` template has been
  moved to `account/account_inactive.html`.

- The adapter API for creating and populating users has been
  overhauled. As a result, the `populate_new_user` adapter methods
  have disappeared. Please refer to the section on "Creating and
  Populating User Instances" for more information.

From 0.12.0
***********

- All account views are now class-based.

- The password reset from key success response now redirects to a
  "done" view (`/accounts/password/reset/key/done/`). This view has
  its own `account/password_reset_from_key_done.html` template. In
  previous versions, the success template was intertwined with the
  `account/password_reset_from_key.html` template.

From 0.11.1
***********

- The `{% provider_login_url %}` tag now takes an optional process
  parameter that indicates how to process the social login. As a
  result, if you include the template
  `socialaccount/snippets/provider_list.html` from your own overriden
  `socialaccount/connections.html` template, you now need to pass
  along the process parameter as follows:
  `{% include "socialaccount/snippets/provider_list.html" with process="connect" %}`.

- Instead of inlining the required Facebook SDK Javascript wrapper
  code into the HTML, it now resides into its own .js file (served
  with `{% static %}`). If you were using the builtin `fbconnect.html`
  this change should go by unnoticed.

From 0.9.0
**********

- Logout no longer happens on GET request. Refer to the `LogoutView`
  documentation for more background information. Logging out on GET
  can be restored by the setting `ACCOUNT_LOGOUT_ON_GET`. Furthermore,
  after logging out you are now redirected to
  `ACCOUNT_LOGOUT_REDIRECT_URL` instead of rendering the
  `account/logout.html` template.

- `LOGIN_REDIRECT_URLNAME` is now deprecated. Django 1.5 accepts both
  URL names and URLs for `LOGIN_REDIRECT_URL`, so we do so as well.

- `DefaultAccountAdapter.stash_email_verified` is now named
  `stash_verified_email`.

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

  - `python manage.py account_unsetmultipleprimaryemails`

    - Will silently remove primary flags for email addresses that
      aren't the same as `user.email`.

    - If no primary `EmailAddress` is `user.email` it will pick one
      at random and print a warning.

- The expiry time, if any, is now stored in a new column
  `SocialToken.expires_at`. Migrations are in place.

- Furthermore, Facebook started returning longer tokens, so the
  maximum token length was increased. Again, migrations are in place.

- Login and signup views have been turned into class-based views.

- The template variable `facebook_perms` is no longer passed to the
  "facebook/fbconnect.html" template. Instead, `fb_login_options`
  containing all options is passed.

From 0.8.3
**********

- `requests` is now a dependency (dropped `httplib2`).

- Added a new column `SocialApp.client_id`. The value of `key` needs
  to be moved to the new `client_id` column. The `key` column is
  required for Stack Exchange. Migrations are in place to handle all
  of this automatically.

From 0.8.2
**********

- The `ACCOUNT_EMAIL_VERIFICATION` setting is no longer a boolean
  based setting. Use a string value of "none", "optional" or
  "mandatory" instead.

- The template "account/password_reset_key_message.txt" has been moved
  to "account/email/password_reset_key_message.txt". The subject of
  the message has been moved into a template
  ("account/email/password_reset_key_subject.txt").

- The `site` foreign key from `SocialApp` to `Site` has been replaced
  by a `ManyToManyField`. Many apps can be used across multiple
  domains (Facebook cannot).


From 0.8.1
**********

- Dropped support for `CONTACT_EMAIL` from the `account` template
  context processor. It was never documented and only used in the
  templates as an example -- there is no need to pollute the `allauth`
  settings with that. If your templates rely on it then you will have
  to put it in a context processor yourself.

From 0.7.0
**********

- `allauth` now depends on Django 1.4 or higher.

- Major impact: dropped dependency on the `emailconfirmation` app, as
  this project is clearly left unmaintained. Important tickets such
  as https://github.com/pinax/django-email-confirmation/pull/5 are not
  being addressed. All models and related functionality have been
  directly integrated into the `allauth.account` app. When upgrading
  take care of the following:

  - The `emailconfirmation` setting `EMAIL_CONFIRMATION_DAYS` has been
    replaced by `ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS`.

  - Instead of directly confirming the e-mail address upon the GET
    request the confirmation is now processed as part of an explicit
    POST. Therefore, a new template `account/email_confirm.html` must
    be setup.

  - Existing `emailconfirmation` data should be migrated to the new
    tables. For this purpose a special management command is
    available: `python manage.py
    account_emailconfirmationmigration`. This command does not drop
    the old `emailconfirmation` tables -- you will have to do this
    manually yourself. Why not use South? EmailAddress uniqueness
    depends on the configuration (`ACCOUNT_UNIQUE_EMAIL`), South does
    not handle settings dependent database models.

- `{% load account_tags %}` is deprecated, simply use: `{% load account %}`

- `{% load socialaccount_tags %}` is deprecated, simply use:
  `{% load socialaccount %}`

From 0.5.0
**********

- The `ACCOUNT_EMAIL_AUTHENTICATION` setting has been dropped in favor
  of `ACCOUNT_AUTHENTICATION_METHOD`.

- The login form field is now always named `login`. This used to by
  either `username` or `email`, depending on the authentication
  method. If needed, update your templates accordingly.

- The `allauth` template tags (containing template tags for
  OpenID, Twitter and Facebook) have been removed. Use the
  `socialaccount` template tags instead (specifically: `{% provider_login_url
  ... %}`).

- The `allauth.context_processors.allauth` context processor has been
  removed, in favor of
  `allauth.socialaccount.context_processors.socialaccount`. In doing
  so, all hardcodedness with respect to providers (e.g
  `allauth.facebook_enabled`) has been removed.


From 0.4.0
**********

- Upgrade your `settings.INSTALLED_APPS`: Replace `allauth.<provider>`
  (where provider is one of `twitter`, `facebook` or `openid`) with
  `allauth.socialaccount.providers.<provider>`

- All provider related models (`FacebookAccount`, `FacebookApp`,
  `TwitterAccount`, `TwitterApp`, `OpenIDAccount`) have been unified
  into generic `SocialApp` and `SocialAccount` models. South migrations
  are in place to move the data over to the new models, after which
  the original tables are dropped. Therefore, be sure to run migrate
  using South.

Providers
=========

Most providers require you to sign up for a so called API client or
app, containing a client ID and API secret. You must add a `SocialApp`
record per provider via the Django admin containing these app
credentials.

When creating the OAuth app on the side of the provider pay special
attention to the callback URL (sometimes also referred to as redirect
URL). If you do not configure this correctly, you will receive login
failures when attempting to log in, such as::

    An error occured while attempting to login via your social network account.

Use a callback URL of the form::

    http://example.com/accounts/twitter/login/callback/
    http://example.com/accounts/soundcloud/login/callback/
    ...

For local development, use the following::

    http://127.0.0.1:8000/accounts/twitter/login/callback/


AngelList
---------

Register your OAuth app here: https://angel.co/api/oauth/clients

For local development, use the following callback URL::

    http://localhost:8000/accounts/angellist/login/callback/


Facebook
--------

For Facebook both OAuth2 and the Facebook Connect Javascript SDK are
supported. You can even mix the two.

Advantage of the Javascript SDK may be a more streamlined user
experience as you do not leave your site. Furthermore, you do not need
to worry about tailoring the login dialog depending on whether or not
you are using a mobile device. Yet, relying on Javascript may not be
everybody's cup of tea.

To initiate a login use::

    {% load socialaccount %}
    <a href="{% provider_login_url "facebook" method="js_sdk" %}">Facebook Connect</a>

or::

    {% load socialaccount %}
    <a href="{% provider_login_url "facebook" method="oauth2" %}">Facebook OAuth2</a>

The following Facebook settings are available::

    SOCIALACCOUNT_PROVIDERS = \
        { 'facebook':
            { 'SCOPE': ['email', 'publish_stream'],
              'AUTH_PARAMS': { 'auth_type': 'reauthenticate' },
              'METHOD': 'oauth2' ,
              'LOCALE_FUNC': 'path.to.callable'} }

METHOD
    Either `js_sdk` or `oauth2`

SCOPE
    By default, `email` scope is required depending whether or not
    `SOCIALACCOUNT_QUERY_EMAIL` is enabled.

AUTH_PARAMS
    Use `AUTH_PARAMS` to pass along other parameters to the `FB.login`
    JS SDK call.

LOCALE_FUNC:
    The locale for the JS SDK is chosen based on the current active language of
    the request, taking a best guess. This can be customized using the
    `LOCALE_FUNC` setting, which takes either a callable or a path to a callable.
    This callable must take exactly one argument, the request, and return `a
    valid Facebook locale <http://developers.facebook.com/docs/
    internationalization/>`_ as a string::

        SOCIALACCOUNT_PROVIDERS = \
            { 'facebook':
                { 'LOCALE_FUNC': lambda request: 'zh_CN'} }

App registration (get your key and secret here)
    https://developers.facebook.com/apps

Development callback URL
    Leave your App Domains empty and put in he section `Website with Facebook
    Login` put this as your Site URL: `http://localhost:8000`


Google
------

The Google provider is OAuth2 based. More info:
`http://code.google.com/apis/accounts/docs/OAuth2.html#Registering`.

You can specify the scope to use as follows::

    SOCIALACCOUNT_PROVIDERS = \
        { 'google':
            { 'SCOPE': ['https://www.googleapis.com/auth/userinfo.profile'],
              'AUTH_PARAMS': { 'access_type': 'online' } }}

By default, `profile` scope is required, and optionally `email` scope
depending on whether or not `SOCIALACCOUNT_QUERY_EMAIL` is enabled.

App registration (get your key and secret here)
        https://code.google.com/apis/console/

Development callback URL
        Make sure you list a redirect uri of the form
        `http://example.com/accounts/google/login/callback/`. You can fill
        multiple URLs, one for each test domain.


LinkedIn
--------

The LinkedIn provider is OAuth based.

You can specify the scope and fields to fetch as follows::

    SOCIALACCOUNT_PROVIDERS = \
        {'linkedin':
          {'SCOPE': ['r_emailaddress'],
           'PROFILE_FIELDS: ['id',
                             'first-name',
                             'last-name',
                             'email-address',
                             'picture-url',
                             'public-profile-url']}}

By default, `r_emailaddress` scope is required depending on whether or
not `SOCIALACCOUNT_QUERY_EMAIL` is enabled.

Note: if you are experiencing issues where it seems as if the scope
has no effect you may be using an old LinkedIn app that is not
scope enabled. Please refer to
`https://developer.linkedin.com/forum/when-will-old-apps-have-scope-parameter-enabled`
for more background information.

App registration (get your key and secret here)
        https://www.linkedin.com/secure/developer?newapp=
Development callback URL
        Leave the OAuth redirect URL empty.

OpenID
------

The OpenID provider does not require any settings per se. However, a
typical OpenID login page presents the user with a predefined list of
OpenID providers and allows the user to input his own OpenID identity
URL in case his provider is not listed by default. The list of
providers displayed by the builtin templates can be configured as
follows::

    SOCIALACCOUNT_PROVIDERS = \
        { 'openid':
            { 'SERVERS':
                [dict(id='yahoo',
                      name='Yahoo',
                      openid_url='http://me.yahoo.com'),
                 dict(id='hyves',
                      name='Hyves',
                      openid_url='http://hyves.nl'),
                 dict(id='google',
                      name='Google',
                      openid_url='https://www.google.com/accounts/o8/id')]}}


If you want to manually include login links yourself, you can use the
following template tag::

    {% load socialaccount %}
    <a href="{% provider_login_url "openid" openid="https://www.google.com/accounts/o8/id" next="/success/url/" %}">Google</a>


Persona
-------

Mozilla Persona does not require any settings. The
`REQUEST_PARAMETERS` dictionary contains optional parameters that are
passed as is to the `navigator.id.request()` method to influence the
look and feel of the Persona dialog::

    SOCIALACCOUNT_PROVIDERS = \
        { 'persona':
            { 'REQUEST_PARAMETERS': {'siteName': 'Example' } } }


SoundCloud
----------

SoundCloud allows you to choose between OAuth1 and OAuth2.  Choose the
latter.


Stack Exchange
--------------

Register your OAuth2 app over at
`http://stackapps.com/apps/oauth/register`.  Do not enable "Client
Side Flow". For local development you can simply use "localhost" for
the OAuth domain.

As for all providers, provider specific data is stored in
`SocialAccount.extra_data`. For Stack Exchange we need to choose what
data to store there by choosing the Stack Exchange site (e.g. Stack
Overflow, or Server Fault). This can be controlled by means of the
`SITE` setting::

    SOCIALACCOUNT_PROVIDERS = \
        { 'stackexchange':
            { 'SITE': 'stackoverflow' } }


Twitch
------
Register your OAuth2 app over at
`http://www.twitch.tv/kraken/oauth2/clients/new`.

Vimeo
-----

App registration
    https://developer.vimeo.com/apps

Development callback URL
    http://localhost:8000


VK
--

App registration
    http://vk.com/apps?act=settings

Development callback URL ("Site address")
    http://localhost


Weibo
-----

Register your OAuth2 app over at
`http://open.weibo.com/apps`. Unfortunately, Weibo does not allow for
specifying a port number in the authorization callback URL. So for
development purposes you have to use a callback url of the form
`http://127.0.0.1/accounts/weibo/login/callback/` and run `runserver
127.0.0.1:80`.



Signals
=======

The following signals are emitted:

- `allauth.account.signals.user_logged_in`

  Sent when a user logs in.

- `allauth.account.signals.user_signed_up`

  Sent when a user signs up for an account. This signal is
  typically followed by a `user_logged_in`, unless e-mail verification
  prohibits the user to log in.

- `allauth.socialaccount.signals.pre_social_login`

  Sent after a user successfully authenticates via a social provider,
  but before the login is fully processed. This signal is emitted as
  part of the social login and/or signup process, as well as when
  connecting additional social accounts to an existing account. Access
  tokens and profile information, if applicable for the provider, is
  provided.

- `allauth.socialaccount.signals.social_account_added`

  Sent after a user connects a social account to a his local account.

- `allauth.socialaccount.signals.social_account_removed`

  Sent after a user disconnects a social account from his local
  account.


Views
=====

Logout
------

The logout view (`allauth.account.views.LogoutView`) requests for
confirmation before logging out. The user is logged out only when the
confirmation is received by means of a POST request.

If you are wondering why, consider what happens when a malicious user
embeds the following image in a post::

    <img src="http://example.com/accounts/logout/">

For this and more background information on the subject, see:

- https://code.djangoproject.com/ticket/15619
- http://stackoverflow.com/questions/3521290/logout-get-or-post

If you insist on having logout on GET, then please consider adding a
bit of Javascript to automatically turn a click on a logout link into
a POST. As a last resort, you can set `ACCOUNT_LOGOUT_ON_GET` to
`True`.

Templates
=========

Template Tags
-------------

The following template tag libraries are available:

- `account`: tags for dealing with accounts in general

- `socialaccount`: tags focused on social accounts


Account Tags
************

Use `user_display` to render a user name without making assumptions on
how the user is represented (e.g. render the username, or first
name?)::

    {% load account %}

    {% user_display user %}

Or, if you need to use in a `{% blocktrans %}`::

    {% load account %}

    {% user_display user as user_display %}
    {% blocktrans %}{{ user_display }} has logged in...{% endblocktrans %}

Then, override the `ACCOUNT_USER_DISPLAY` setting with your project
specific user display callable.


Social Account Tags
*******************

Use the `provider_login_url` tag to generate provider specific login URLs::

    {% load socialaccount %}

    <a href="{% provider_login_url "openid" openid="https://www.google.com/accounts/o8/id" next="/success/url/" %}">Google</a>
    <a href="{% provider_login_url "twitter" %}">Twitter</a>

Here, you can pass along an optional `process` parameter that
indicates how to process the social login. You can choose between
`login` and `connect`::

    <a href="{% provider_login_url "twitter" process="connect" %}">Connect a Twitter account</a>

Furthermore, you can pass along an `action` parameter with value
`reauthenticate` to indicate that you want the user to be re-prompted
for authentication even if he already signed in before. For now, this
is supported by Facebook, Google and Twitter only.


For easy access to the social accounts for a user::

    {% get_social_accounts user as accounts %}

Then::

    {{accounts.twitter}} -- a list of connected Twitter accounts
    {{accounts.twitter.0}} -- the first Twitter account
    {% if accounts %} -- if there is at least one social account

Decorators
==========

Verified E-mail Required
------------------------

Even when email verification is not mandatory during signup, there
may be circumstances during which you really want to prevent
unverified users to proceed. For this purpose you can use the
following decorator::

    from allauth.account.decorators import verified_email_required

    @verified_email_required
    def verified_users_only_view(request):
        ...

The behavior is as follows:

- If the user isn't logged in, it acts identical to the
  `login_required` decorator.

- If the user is logged in but has no verified e-mail address, an
  e-mail verification mail is automatically resend and the user is
  presented with a page informing him he needs to verify his email
  address.


Advanced Usage
==============

Custom User Models
------------------

If you use a custom user model you need to specify what field
represents the `username`, if any. Here, `username` really refers to
the field representing the nick name the user uses to login, and not
some unique identifier (possibly including an e-mail adddress) as is
the case for Django's `AbstractBaseUser.USERNAME_FIELD`.

Meaning, if your custom user model does not have a `username` field
(again, not to be mistaken with an e-mail address or user id), you
will need to set `ACCOUNT_USER_MODEL_USERNAME_FIELD` to `None`. This
will disable username related functionality in `allauth`.

Similarly, you will need to set `ACCOUNT_USER_MODEL_EMAIL_FIELD` to
`None`, or the proper field (if other than `email`).


Creating and Populating User instances
--------------------------------------

The following adapter methods can be used to intervene in how User
instances are created, and populated with data

- `allauth.account.adapter.DefaultAccountAdapter`:

  - `new_user(self, request)`: Instantiates a new, empty `User`.

  - `save_user(self, request, user, form)`: Populates and saves the
    `User` instance using information provided in the signup form.

- `allauth.socialaccount.adapter.DefaultSocialAccountAdapter`:

  - `new_user(self, request, sociallogin)`: Instantiates a new, empty
    `User`.

  - `save_user(self, request, sociallogin, form=None)`: Populates and
    saves the `User` instance (and related social login data). The
    signup form is not available in case of auto signup.

  - `populate_user(self, request, sociallogin, data)`: Hook that can
    be used to further populate the user instance
    (`sociallogin.account.user`). Here, `data` is a dictionary of
    common user properties (`first_name`, `last_name`, `email`,
    `username`, `name`) that the provider already extracted for you.


Invitations
-----------

Invitation handling is not supported, and most likely will not be any
time soon. An invitation app could cover anything ranging from
invitations of new users, to invitations of existing users to
participate in restricted parts of the site. All in all, the scope of
invitation handling is large enough to warrant being addressed in an
app of its own.

Still, everything is in place to easily hook up any third party
invitation app. The account adapter
(`allauth.account.adapter.DefaultAccountAdapter`) offers the following
methods:

- `is_open_for_signup(self, request)`. You can override this method to, for
  example, inspect the session to check if an invitation was accepted.

- `stash_verified_email(self, request, email)`. If an invitation was
  accepted by following a link in a mail, then there is no need to
  send e-mail verification mails after the signup is completed. Use
  this method to record the fact that an e-mail address was verified.


Sending E-mail
--------------

E-mails sent (e.g. in case of password forgotten, or e-mail
confirmation) can be altered by providing your own
templates. Templates are named as follows::

    account/email/email_confirmation_subject.txt
    account/email/email_confirmation_message.txt

In case you want to include an HTML representation, add an HTML
template as follows::

    account/email/email_confirmation_message.html

If this does not suit your needs, you can hook up your own custom
mechanism by overriding the `send_mail` method of the account adapter
(`allauth.account.adapter.DefaultAccountAdapter`).


Custom Redirects
----------------

If redirecting to statically configurable URLs (as specified in your
project settings) is not flexible enough, then you can override the
following adapter methods:

- `allauth.account.adapter.DefaultAccountAdapter`:

  - `get_login_redirect_url(self, request)`

  - `get_logout_redirect_url(self, request)`

  - `get_email_confirmation_redirect_url(self, request)`

- `allauth.socialaccount.adapter.DefaultSocialAccountAdapter`:

  - `get_connect_redirect_url(self, request, socialaccount)`

For example, redirecting to `/accounts/<username>/` can be implemented as
follows::

    # project/settings.py:
    ACCOUNT_ADAPTER = 'project.users.adapter.MyAccountAdapter'

    # project/users/adapter.py:
    from django.conf import settings
    from allauth.account.adapter import DefaultAccountAdapter

    class MyAccountAdapter(DefaultAccountAdapter):

        def get_login_redirect_url(self, request):
            path = "/accounts/{username}/"
            return path.format(username=request.user.username)

Messages
--------

The Django messages framework (`django.contrib.messages`) is used if
it is listed in `settings.INSTALLED_APPS`.  All messages (as in
`django.contrib.messages`) are configurable by overriding their
respective template. If you want to disable a message simply override
the message template with a blank one.


Frequently Asked Questions
==========================

Overall
-------

Why don't you implement support for ... ?
*****************************************

This app is just about authentication. Anything that is project
specific, such as making choices on what to display in a profile page,
or, what information is stored for a user (e.g. home address, or
favorite color?), is beyond scope and therefore not offered.

This information is nice and all, but... I need more!
*****************************************************

Here are a few third party resources to help you get started:

- https://speakerdeck.com/tedtieken/signing-up-and-signing-in-users-in-django-with-django-allauth
- http://stackoverflow.com/questions/tagged/django-allauth
- http://www.sarahhagstrom.com/2013/09/the-missing-django-allauth-tutorial/

Troubleshooting
---------------

The /accounts/ URL is giving me a 404
*************************************

There is no such URL. Try `/accounts/login/` instead.

When I attempt to login I run into a 404 on /accounts/profile/
**************************************************************

When you end up here you have successfully logged in. However, you
will need to implement a view for this URL yourself, as whatever is to
be displayed here is project specific. You can also decide to redirect
elsewhere:

https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url

When I sign up I run into connectivity errors (connection refused et al)
************************************************************************

You probably have not got an e-mail (SMTP) server running on the
machine you are developing on. Therefore, `allauth` is unable to send
verification mails.

You can work around this by adding the following line to
``settings.py``:

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

This will avoid the need for an SMTP server as e-mails will be printed
to the console. For more information, please refer to:

https://docs.djangoproject.com/en/dev/ref/settings/#email-host

Showcase
========

- http://www.highlightcam.com/
- http://www.q-dance.com
- http://officecheese.com
- http://www.mycareerstack.com
- http://jug.gl
- http://www.charityblossom.org/
- http://www.superreceptionist.in
- http://www.edithuddle.com
- http://kwatsi.com
- http://www.smartgoalapp.com
- http://www.neekanee.com/
- http://healthifyme.com/
- http://www.burufly.com
- http://eatwith.com/
- http://en.globalquiz.org/
- ...

Please mail me (raymond.penners@intenct.nl) links to sites that have
`django-allauth` up and running.


Commercial Support
==================

This project is sponsored by IntenCT_. If you require assistance on
your project(s), please contact us: info@intenct.nl.

.. _IntenCT: http://www.intenct.info
