Rate Limits
===========

In order to be secure out of the box various rate limits are in place. The rate
limit mechanism is backed by a Django cache. Hence, rate limiting will not work
properly if you are using the `DummyCache`.

When rate limits are hit the ``429.html`` template is rendered,
alternatively, you can configure a custom handler by declaring
a ``handler429`` view in your root URLconf.

Rate limits are consumed by triggering actions, the full list of which is
documented below.  Per action, the rate can be configured. The rate itself is an
amount, per time unit, per either IP address, user or action-specific key.

For example, requesting a password reset is an action that is both limited
globally by IP address, as well as per email. Here, the email address used is
the specific key.

The rate limits are configured through the ``ACCOUNT_RATE_LIMITS`` setting:

- Set it to ``False`` to disable all rate limits.

- Set it to a dictionary, e.g. ``{"action": "your-rate-limit", ...}`` to use the
  default configuration but with your specific actions overriden.


The following actions are available for configuration:

``"change_password"`` (default: ``"5/m/user"``)
  Changing the password (for already authenticated users).

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
  while this protects the allauth login view, it does not protect Django's admin
  login from being brute forced. Note that a successful login will clear this
  rate limit.

``"confirm_email"`` (default: ``"1/3m/key"`` (link) or ``"1/10s/key"`` (code))
  Users can request email confirmation mails via the email management view, and,
  implicitly, when logging in with an unverified account. This rate limit
  prevents users from sending too many of these mails.


Additional notes:

Unless the rate limit is disabled or the default limits are increased, you might
run intro problems if you're running unit tests that are dependant on
funcionalities covered by the rate limits. For example, if you're testing the
`confirm_email` functionality in your unit tests and you're testing if the
verification email is sent twice after requesting it twice, only one of the
emails will be sent.
