Advanced Usage
==============

Custom User Models
------------------

If you use a custom user model you need to specify what field
represents the ``username``, if any. Here, ``username`` really refers to
the field representing the nickname that the user uses to login, and not to
some unique identifier (possibly including an email address) as is
the case for Django's ``AbstractBaseUser.USERNAME_FIELD``.

Therefore, if your custom user model does not have a ``username`` field
(again, not to be mistaken with an email address or user id), you
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
    ACCOUNT_LOGIN_METHODS = {'email'}


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


Custom Redirects
----------------

If redirecting to statically configurable URLs (as specified in your
project settings) is not flexible enough, then you can override the
following adapter methods:

- ``allauth.account.adapter.DefaultAccountAdapter``:

  - ``get_login_redirect_url(self, request)``

  - ``get_logout_redirect_url(self, request)``

  - ``get_email_verification_redirect_url(self, email_address)``

  - ``get_signup_redirect_url(self, request)``

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
