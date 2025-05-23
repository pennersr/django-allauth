Rate Limits
===========

In this section the ratelimits related to the ``allauth.account`` app are
documented.  Refer to the :doc:`overall rate limit documentation <../common/rate_limits>`
for more background information on the mechanism itself.

The rate limits are configured through the ``ACCOUNT_RATE_LIMITS`` setting:

- Set it to ``False`` to disable all rate limits.

- Set it to a dictionary, e.g. ``{"action": "your-rate-limit", ...}`` to use the
  default configuration but with your specific actions overriden.


The following actions are available for configuration:

``"change_password"`` (default: ``"5/m/user"``)
  Changing the password (for already authenticated users).

``"change_phone"`` (default: ``"1/m/user"``)
  Changing the phone number.

``"manage_email"`` (default: ``"10/m/user"``)
  Email management related actions, such as add, remove, change primary.

``"reset_password"`` (default: ``"20/m/ip,5/m/key"``)
  Requesting a password reset. The email for which the password is to be reset is
  passed as the key.

``"reauthenticate"`` (default: ``"10/m/user"``)
  Reauthentication (for users already logged in).

``"reset_password_from_key"`` (default: ``"20/m/ip"``)
  Password reset (the view the password reset email links to).

``"signup"`` (default: ``"20/m/ip"``)
  Signups.

``"login"`` (default: ``"30/m/ip"``)
  Logins.

``"login_failed"`` (default: ``"10/m/ip,5/5m/key"``)
  Restricts the allowed number of failed login attempts. When exceeded, the user
  is prohibited from logging in for the remainder of the rate limit. Important:
  while this protects the allauth login view, it does not
  :doc:`protect Django's admin login from being brute forced <../common/admin>`.

``"confirm_email"`` (default: ``"1/3m/key"`` (link) or ``"1/10s/key"`` (code))
  Users can request email confirmation mails via the email management view, and,
  implicitly, when logging in with an unverified account. This rate limit
  prevents users from sending too many of these mails.
