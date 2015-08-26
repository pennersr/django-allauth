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
