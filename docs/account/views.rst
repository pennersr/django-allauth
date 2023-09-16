Views
=====

Login
-----

*URL name*:
  ``account_login``

Users login via the ``allauth.account.views.LoginView`` view over at
``/accounts/login/`` (URL name ``account_login``). When users attempt to login
while their account is inactive (``user.is_active``) they are presented with the
``account/account_inactive.html`` template.


Signup
------

*URL name*:
  ``account_signup``

Users sign up via the ``allauth.account.views.SignupView`` view over at
``/accounts/signup/`` (URL name ``account_signup``).


Logout
------

*URL name*:
  ``account_logout``

The logout view (``allauth.account.views.LogoutView``) over at
``/accounts/logout/`` (URL name ``account_logout``) requests for confirmation
before logging out. The user is logged out only when the confirmation is
received by means of a POST request.

If you are wondering why, consider what happens when a malicious user
embeds the following image in a post::

    <img src="http://example.com/accounts/logout/">

For this and more background information on the subject, see:

- https://code.djangoproject.com/ticket/15619
- http://stackoverflow.com/questions/3521290/logout-get-or-post

If you insist on having logout on GET, then please consider adding a
bit of Javascript to automatically turn a click on a logout link into
a POST. As a last resort, you can set ``ACCOUNT_LOGOUT_ON_GET`` to
``True``.


Password Management
-------------------

Authenticated users can manage their password account using the
``allauth.account.views.PasswordSetView`` and
``allauth.account.views.PasswordChangeView`` views, over at
``/accounts/password/set/`` respectively ``/accounts/password/change/`` (URL names
``account_set_password`` and ``account_change_password`` respectively).

Users are redirected between these views, according to whether or not
they have setup a password (``user.has_usable_password()``).  Typically,
when users signup via a social provider they will not have a password
set.


Password Reset
--------------

*URL name*:
  ``account_reset_password``

Users can request a password reset using the
``allauth.account.views.PasswordResetView`` view over at
``/accounts/password/reset/`` (URL name ``account_reset_password``).  An email
will be sent containing a reset link pointing to ``PasswordResetFromKeyView``
view.


Emails Management
-----------------

*URL name*:
  ``account_email``

Users manage the email addresses tied to their account using the
``allauth.account.views.EmailView`` view over at ``/accounts/email/`` (URL name
``account_email``). Here, users can add (and verify) email addresses, remove
email addresses, and choose a new primary email address.


Email Verification
-------------------

Depending on the setting ``ACCOUNT_EMAIL_VERIFICATION``, a verification
email is sent pointing to the
``allauth.account.views.ConfirmEmailView`` view.

The setting ``ACCOUNT_CONFIRM_EMAIL_ON_GET`` determines whether users
have to manually confirm the address by submitting a confirmation form,
or whether the address is automatically confirmed by a mere GET
request.
