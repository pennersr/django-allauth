==========================
Welcome to django-allauth!
==========================

Integrated set of Django applications addressing authentication,
registration, account management as well as 3rd party (social) account
authentication.

Rationale
=========

Why?
----

Most existing Django apps that address the problem of social
authentication focus on just that. You typically need to integrate
another app in order to support authentication via a local
account. 

This approach separates the worlds of local and social
authentication. However, there are common scenarios to be dealt with
in boh worlds. For example, an e-mail address passed along by an
OpenID provider is not guaranteed to be verified. So, before hooking
an OpenID account up to a local account the e-mail address must be
verified. So, e-mail verification needs to be present in both worlds.

Integrating both worlds is quite a tedious process. It is definately
not a matter of simply adding one social authentication app, and one
local account registration app to your `INSTALLED_APPS` list.

This is the reason this project got started -- to offer a fully
integrated authentication app that allows for both local and social
authentication, with flows that just work.


Why Not?
--------

From the start the focus has been to deliver an integrated experience
and flows that just work, and to a lesser extent a completely
pluggable social authentication framework.

Earlier versions of the project suffered from this, e.g. each provider
had its own implementation with its own social account model
definition. 

Work is well underway to rectify this situation. These days, social
account models have been unified, and adding support for additional
OAuth/OAuth2 providers is child's play. All hardcodedness with respect
to providers has been removed.

Ofcourse, there is always more that can be done. Do know that the
biggest hurdles to overcome the initial shortcomings have been
taken...

Overview
========

Supported Flows
---------------

- Signup of a both local and social accounts

- Connecting more than one social account to a local account

- Disconnecting a social account -- requires setting a password if
  only the local account remains

- Optional instant-signup for social accounts -- no questions asked

- E-mail address management (multiple e-mail addresses, setting a primary)

- Password forgotten flow

- E-mail address verification flow

Supported Providers
-------------------

- Facebook (both OAuth2 and JS SDK)

- Github

- Google (OAuth2)

- LinkedIn

- OpenId

- Twitter

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
        "allauth.socialaccount.context_processors.socialaccount"
    )

    AUTHENTICATION_BACKENDS = ( ...
        "allauth.account.auth_backends.AuthenticationBackend", )

    INSTALLED_APPS = (
        ...
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.github',
        'allauth.socialaccount.providers.linkedin',
        'allauth.socialaccount.providers.openid',
        'allauth.socialaccount.providers.twitter',
        'emailconfirmation',

urls.py::

    urlpatterns = patterns('',
        ...
        (r'^accounts/', include('allauth.urls')))


Configuration
-------------

Available settings:

ACCOUNT_AUTHENTICATION_METHOD (="username" | "email" | "username_email")
  Specifies the login method to use -- whether the user logs in by
  entering his username, e-mail address, or either one of both.

ACCOUNT_EMAIL_REQUIRED (=False)
  The user is required to hand over an e-mail address when signing up.

ACCOUNT_EMAIL_VERIFICATION (=False)
  After signing up, keep the user account inactive until the e-mail
  address is verified.

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

ACCOUNT_USER_DISPLAY (=a callable returning `user.username`)
  A callable (or string of the form `'some.module.callable_name'`)
  that takes a user as its only argument and returns the display name
  of the user. The default implementation returns `user.username`.

ACCOUNT_PASSWORD_INPUT_RENDER_VALUE (=False)
  `render_value` parameter as passed to `PasswordInput` fields.

ACCOUNT_PASSWORD_MIN_LENGTH (=6)
  An integer specifying the minimum password length.

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

SOCIALACCOUNT_PROVIDERS (= dict)
    Dictionary containing provider specific settings.

EMAIL_CONFIRMATION_DAYS (=# of days, no default)
  Determines the expiration date of email confirmation mails sent by
  django-email-confirmation.


Upgrading
---------

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

    {% load socialaccount_tags %}
    <a href="{% provider_login_url "facebook" method="js_sdk" %}">Facebook Connect</a>

or::

    {% load socialaccount_tags %}
    <a href="{% provider_login_url "facebook" method="oauth2" %}">Facebook OAuth2</a>

The following Facebook settings are available::

    SOCIALACCOUNT_PROVIDERS = \
        { 'facebook': 
            { 'SCOPE': ['email', 'publish_stream'],
              'METHOD': 'oauth2' } }

By default, `email` scope is required depending whether or not
`SOCIALACCOUNT_QUERY_EMAIL` is enabled.

Google
------

The Google provider is OAuth2 based. Register your Google API client
over at `https://code.google.com/apis/console/`. Make sure you list a
redirect uri of the form
`http://example.com/accounts/google/login/callback/`.

You can specify the scope to use as follows::

    SOCIALACCOUNT_PROVIDERS = \
        { 'google': 
            { 'SCOPE': ['https://www.googleapis.com/auth/userinfo.profile'] } }

By default, `profile` scope is required, and optionally `email` scope
depending on whether or not `SOCIALACCOUNT_QUERY_EMAIL` is enabled.



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

    {% load socialaccount_tags %}
    <a href="{% provider_login_url "openid" openid="https://www.google.com/accounts/o8/id" next="/success/url/" %}">Google</a>


Templates
=========

Template Tags
-------------

The following template tag libraries are available:

- `account_tags`: tags for dealing with accounts in general

- `socialaccount_tags`: tags focused on social accounts


Account Tags
************

Use `user_display` to render a user name without making assumptions on
how the user is represented (e.g. render the username, or first
name?)::

    {% load account_tags %}

    {% user_display user %}

Or, if you need to use in a `{% blocktrans %}`::

    {% load account_tags %}

    {% user_display user as user_display}
    {% blocktrans %}{{ user_display }} has logged in...{% endblocktrans %}

Then, override the `ACCOUNT_USER_DISPLAY` setting with your project
specific user display callable.


Social Account Tags
*******************

Use the `provider_login_url` tag to generate provider specific login URLs::

    {% load socialaccount_tags %}

    <a href="{% provider_login_url "openid" openid="https://www.google.com/accounts/o8/id" next="/success/url/" %}">Google</a>
    <a href="{% provider_login_url "twitter" %}">Twitter</a>


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



Showcase
========

- http://officecheese.com
- http://www.mycareerstack.com
- http://jug.gl
- http://www.charityblossom.org/
- ...

Please mail me (raymond.penners@intenct.nl) links to sites that have
`django-allauth` up and running.
