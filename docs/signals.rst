Signals
=======

There are several signals emitted during authentication flows. You can
hook to them for your own needs.


allauth.account
---------------


- `allauth.account.signals.user_logged_in`

  Sent when a user logs in.

- `allauth.account.signals.user_signed_up`

  Sent when a user signs up for an account. This signal is
  typically followed by a `user_logged_in`, unless e-mail verification
  prohibits the user to log in.

- `allauth.account.signals.password_set`

  Sent when a password has been successfully set for the first time.

- `allauth.account.signals.password_changed`

  Sent when a password has been successfully changed.

- `allauth.account.signals.password_reset`

  Sent when a password has been successfully reset.

- `allauth.account.signals.email_confirmed`

  Sent after the email address in the db was updated and set to confirmed.

- `allauth.account.signals.email_confirmation_sent`

  Sent right after the email confirmation is sent.

- `allauth.account.signals.email_changed`

  Sent when a primary email address has been changed.

- `allauth.account.signals.email_added`

  Sent when a new email address has been added.

- `allauth.account.signals.email_removed`

  Sent when an email address has been deleted.


allauth.socialaccount
---------------------

- `allauth.socialaccount.signals.pre_social_login`

  Sent after a user successfully authenticates via a social provider,
  but before the login is fully processed. This signal is emitted as
  part of the social login and/or signup process, as well as when
  connecting additional social accounts to an existing account. Access
  tokens and profile information, if applicable for the provider, is
  provided.

- `allauth.socialaccount.signals.social_account_added`

  Sent after a user connects a social account to a their local account.

- `allauth.socialaccount.signals.social_account_removed`

  Sent after a user disconnects a social account from their local
  account.
