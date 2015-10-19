Views
=====

Login
-----

URL for login view (`allauth.account.views.LoginView`) is `/accounts/login/`.
Pre-arranged template show login form and social login links for installed providers.

User can login or create account with social provider. In case of creating new account, system
checks uniqueness of provided e-mail address. If an account with same e-mail has already exist,
the user is redirected to `allauth.socialaccount.views.SignupView` view.
In this view user have to select unique username and unique e-mail.
We cannot simply connect social account to the existing user. Reason is that the
e-mail adress may not be verified, meaning, the user may be a hacker that has added your
e-mail address to their account in the hope that you fall in their trap.  We cannot
check on 'email_address.verified' either, because 'email_address' is not guaranteed to
be verified. Automatic coupling is discussed in https://github.com/pennersr/django-allauth/issues/215

If user tries to login to inactive account, `allauth.templates.account.account_inactive.html` template is shown.

If problem appears during social provider login `templates/socialaccount/login_cancelled.html`
or `templates/socialaccount/authentication_error.html` is shown.


Signup
------

URL for sign up is (`allauth.account.views.SignupView`) is `/accounts/signup/`.
Pre-arranged template shows sign up form.


Logout
------

The logout view (`allauth.account.views.LogoutView`) requests for
confirmation before logging out. The user is logged out only when the
confirmation is received by means of a POST request. Default URL is `/accounts/logout/`.

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


Password set and change
-----------------------

Authenticated user can manage password account with
`allauth.account.views.PasswordSetView` and `allauth.account.views.PasswordChangeView` views.
URLs for views are `/accounts/password/set/` and `/accounts/password/change/`.

User is redirected between these views, according password is set or not set for the account. 
If the account already have a password, user is redirected to password change view.
If the account do not have a password (for instance is created by social provider), user is redirected to password set view.


Password reset
--------------

User can request reset of his password with `allauth.account.views.PasswordResetView` view.
System sends e-mail with reset link point to `PasswordResetFromKeyView` view.


E-mails settings
----------------

With view `allauth.account.views.EmailView` user can manage account e-mails. One account can be connected with several
e-mails. User can add, remove, choose primary and verificate e-mail addresses. URL is `/accounts/email/`.   


E-mail verification
-------------------

According of configuration `ACCOUNT_EMAIL_VERIFICATION`, system sends verification e-mails with link to
`allauth.account.views.ConfirmEmailView` view. 
 
Configuration `ACCOUNT_CONFIRM_EMAIL_ON_GET`, determines whether or not an e-mail address
is automatically confirmed by a mere GET request. Configuration `ACCOUNT_CONFIRM_EMAIL_ON_GET`,
determines whether user have to confirm address by submiting form or
an e-mail address is automatically confirmed by a mere GET request.


Social connections
------------------

With `allauth.socialaccount.views.ConnectionsView` view user can manage social provider connections.
User can add or remove connections. URL is `/accounts/social/connections/`. 
