Advanced Usage
==============


HTTPS
-----

This app currently provides no functionality for enforcing views to be
HTTPS only, or switching from HTTP to HTTPS (and back) on demand.
There are third party packages aimed at providing precisely this,
please use these .

What is provided is the following:

- The protocol to be used for generating links (e.g. password
  forgotten) for e-mails is configurable by means of the
  `ACCOUNT_DEFAULT_HTTP_PROTOCOL` setting.

- Automatically switching to HTTPS is built-in for OAuth providers
  that require this (e.g. Amazon). However, remembering the original
  protocol before the switch and switching back after the login is not
  provided.


Custom User Models
------------------

If you use a custom user model you need to specify what field
represents the `username`, if any. Here, `username` really refers to
the field representing the nick name the user uses to login, and not
some unique identifier (possibly including an e-mail address) as is
the case for Django's `AbstractBaseUser.USERNAME_FIELD`.

Meaning, if your custom user model does not have a `username` field
(again, not to be mistaken with an e-mail address or user id), you
will need to set `ACCOUNT_USER_MODEL_USERNAME_FIELD` to `None`. This
will disable username related functionality in `allauth`. Remember to
also to set `ACCOUNT_USERNAME_REQUIRED` to `False`.

Similarly, you will need to set `ACCOUNT_USER_MODEL_EMAIL_FIELD` to
`None`, or the proper field (if other than `email`).

For example, if you want to use a custom user model that has `email`
as the identifying field, and you don't want to collect usernames, you
need the following in your settings.py::

    ACCOUNT_USER_MODEL_USERNAME_FIELD = None
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_USERNAME_REQUIRED = False
    ACCOUNT_AUTHENTICATION_METHOD = 'email'


Creating and Populating User instances
--------------------------------------

The following adapter methods can be used to intervene in how User
instances are created, and populated with data

- `allauth.account.adapter.DefaultAccountAdapter`:

  - `is_open_for_signup(self, request)`: The default function
  returns `True`. You can override this method by returning `False`
  if you want to disable account signup.

  - `new_user(self, request)`: Instantiates a new, empty `User`.

  - `save_user(self, request, user, form)`: Populates and saves the
    `User` instance using information provided in the signup form.

  - `populate_username(self, request, user)`:
    Fills in a valid username, if required and missing.  If the
    username is already present it is assumed to be valid (unique).

  - `confirm_email(self, request, email_address)`: Marks the email address as
    confirmed and saves to the db.

  - `generate_unique_username(self, txts, regex=None)`: Returns a unique username
    from the combination of strings present in txts iterable. A regex pattern
    can be passed to the method to make sure the generated username matches it.

- `allauth.socialaccount.adapter.DefaultSocialAccountAdapter`:

  - `is_open_for_signup(self, request)`: The default function
  returns that is the same as `ACCOUNT_ADAPTER` in `settings.py`.
  You can override this method by returning `True`/`False`
  if you want to enable/disable socialaccount signup.

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

The project does not contain any HTML email templates out of the box.
When you do provide these yourself, note that both the text and HTML
versions of the message are sent.

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
