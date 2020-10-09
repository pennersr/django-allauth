Advanced Usage
==============


HTTPS
-----

This app currently provides no functionality for enforcing views to be
HTTPS only, or switching from HTTP to HTTPS (and back) on demand.
There are third party packages aimed at providing precisely this,
so please use these.

What is provided is the following:

- The protocol to be used for generating links (e.g. password
  forgotten) for e-mails is configurable by means of the
  ``ACCOUNT_DEFAULT_HTTP_PROTOCOL`` setting.

- Automatically switching to HTTPS is built-in for OAuth providers
  that require this (e.g. Amazon). However, remembering the original
  protocol before the switch and switching back after the login is not
  provided.


Custom User Models
------------------

If you use a custom user model you need to specify what field
represents the ``username``, if any. Here, ``username`` really refers to
the field representing the nickname that the user uses to login, and not to
some unique identifier (possibly including an e-mail address) as is
the case for Django's ``AbstractBaseUser.USERNAME_FIELD``.

Therefore, if your custom user model does not have a ``username`` field
(again, not to be mistaken with an e-mail address or user id), you
will need to set ``ACCOUNT_USER_MODEL_USERNAME_FIELD`` to ``None``. This
will disable username related functionality in ``allauth``. Remember to
also set ``ACCOUNT_USERNAME_REQUIRED`` to ``False``.

Similarly, you will need to set ``ACCOUNT_USER_MODEL_EMAIL_FIELD`` to
``None`` or to the proper field (if other than ``email``).

For example, if you want to use a custom user model that has ``email``
as the identifying field, and you don't want to collect usernames, you
need the following in your settings.py::

    ACCOUNT_USER_MODEL_USERNAME_FIELD = None
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_USERNAME_REQUIRED = False
    ACCOUNT_AUTHENTICATION_METHOD = 'email'


Creating and Populating User instances
--------------------------------------

The following adapter methods can be used to intervene in how User
instances are created and populated with data

- ``allauth.account.adapter.DefaultAccountAdapter``:

  - ``is_open_for_signup(self, request)``: The default function
    returns ``True``. You can override this method by returning ``False``
    if you want to disable account signup.

  - ``new_user(self, request)``: Instantiates a new, empty ``User``.

  - ``save_user(self, request, user, form)``: Populates and saves the
    ``User`` instance using information provided in the signup form.

  - ``populate_username(self, request, user)``:
    Fills in a valid username, if required and missing.  If the
    username is already present, then it is assumed to be valid (unique).

  - ``confirm_email(self, request, email_address)``: Marks the email address as
    confirmed and saves to the db.

  - ``generate_unique_username(self, txts, regex=None)``: Returns a unique username
    from the combination of strings present in txts iterable. A regex pattern
    can be passed to the method to make sure the generated username matches it.

- ``allauth.socialaccount.adapter.DefaultSocialAccountAdapter``:

  - ``is_open_for_signup(self, request, socialaccount)``: The default function
    returns that is the same as ``ACCOUNT_ADAPTER`` in ``settings.py``.
    You can override this method by returning ``True``/``False``
    if you want to enable/disable socialaccount signup.

  - ``new_user(self, request, sociallogin)``: Instantiates a new, empty
    ``User``.

  - ``save_user(self, request, sociallogin, form=None)``: Populates and
    saves the ``User`` instance (and related social login data). The
    signup form is not available in case of auto signup.

  - ``populate_user(self, request, sociallogin, data)``: Hook that can
    be used to further populate the user instance
    (``sociallogin.account.user``). Here, ``data`` is a dictionary of
    common user properties (``first_name``, ``last_name``, ``email``,
    ``username``, ``name``) that the provider already extracted for you.


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
(``allauth.account.adapter.DefaultAccountAdapter``) offers the following
methods:

- ``is_open_for_signup(self, request)``. You can override this method to, for
  example, inspect the session to check if an invitation was accepted.

- ``stash_verified_email(self, request, email)``. If an invitation was
  accepted by following a link in an email, then there is no need to
  send email verification mails after the signup is completed. Use
  this method to record the fact that an email address was verified.


Sending Email
--------------

Emails sent (e.g. in case of password forgotten or email
confirmation) can be altered by providing your own
templates. Templates are named as follows::

    account/email/email_confirmation_signup_subject.txt
    account/email/email_confirmation_signup_message.txt

    account/email/email_confirmation_subject.txt
    account/email/email_confirmation_message.txt

In case you want to include an HTML representation, add an HTML
template as follows::

    account/email/email_confirmation_signup_message.html

    account/email/email_confirmation_message.html

The project does not contain any HTML email templates out of the box.
When you do provide these yourself, note that both the text and HTML
versions of the message are sent.

If this does not suit your needs, you can hook up your own custom
mechanism by overriding the ``send_mail`` method of the account adapter
(``allauth.account.adapter.DefaultAccountAdapter``).


Custom Redirects
----------------

If redirecting to statically configurable URLs (as specified in your
project settings) is not flexible enough, then you can override the
following adapter methods:

- ``allauth.account.adapter.DefaultAccountAdapter``:

  - ``get_login_redirect_url(self, request)``

  - ``get_logout_redirect_url(self, request)``

  - ``get_email_confirmation_redirect_url(self, request)``

- ``allauth.socialaccount.adapter.DefaultSocialAccountAdapter``:

  - ``get_connect_redirect_url(self, request, socialaccount)``

For example, redirecting to ``/accounts/<username>/`` can be implemented as
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

The Django messages framework (``django.contrib.messages``) is used if
it is listed in ``settings.INSTALLED_APPS``.  All messages (as in
``django.contrib.messages``) are configurable by overriding their
respective template. If you want to disable a message, simply override
the message template with a blank one.

Admin
-----

The Django admin site (``django.contrib.admin``) does not use Django allauth by
default. Since Django admin provides a custom login view, it does not go through
the normal Django allauth workflow.

.. warning::

    This limitation means that Django allauth features are not applied to the
    Django admin site:

    * ``ACCOUNT_LOGIN_ATTEMPTS_LIMIT`` and ``ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT`` do not
      protect Django’s admin login from being brute forced.
    * Any other custom workflow that overrides the Django allauth adapter's
      login method will not be applied.

An easy workaround for this is to require users to login before going to the
Django admin site's login page (note that the following would need to be applied to
every instance of ``AdminSite``):

.. code-block:: python

    from django.contrib import admin
    from django.contrib.auth.decorators import login_required

    admin.site.login = login_required(admin.site.login)

Customizing providers
---------------------

When an existing provider doesn't quite meet your needs, you might find yourself
needing to customize a provider.

This can be achieved by subclassing an existing provider and making your changes
there. Providers are defined as django applications, so typically customizing one
will mean creating a django application in your project.  This application will contain your customized
urls.py, views.py and provider.py files. The behaviour that can be customized is beyond
the scope of this documentation.

.. warning::

    In your ``provider.py`` file, you will need to expose the provider class
    by having a module level attribute called ``provider_classes`` with your custom
    classes in a list. This allows your custom provider to be registered properly
    on the basis of the ``INSTALLED_APPS`` setting.

    Be sure to use a custom id property on your provider class such that its default
    URLs do not clash with the provider you are subclassing.

.. code-block:: python

    class GoogleNoDefaultScopeProvider(GoogleProvider):
        id = 'google_no_scope'

        def get_default_scope(self):
            return []

    provider_classes = [GoogleNoDefaultScopeProvider]

Changing provider scopes
------------------------

Some projects may need more scopes than the default required for authentication purposes.

Scopes can be modified via ``SOCIALACCOUNT_PROVIDERS`` in your project settings.py file.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        '<ProviderNameHere>': {
            'SCOPE': [...]
        }
    }

You need to obtain the default scopes that allauth uses by
looking in ``allauth/socialaccount/providers/<ProviderNameHere>/provider.py``
and look for ``def get_default_scope(self):`` method. Copy those default scopes
into the SCOPE list shown above.

Example of adding calendar.readonly scope to Google scopes::

    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'SCOPE': [
                'profile',
                'email',
                'openid',
                'https://www.googleapis.com/auth/calendar.readonly'
            ],
        }
    }
