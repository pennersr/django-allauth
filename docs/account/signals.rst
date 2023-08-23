Signals
=======

There are several signals emitted during authentication flows. You can
hook to them for your own needs.


- ``allauth.account.signals.user_logged_in(request, user)``
    Sent when a user logs in.

- ``allauth.account.signals.user_logged_out(request, user)``
    Sent when a user logs out.

- ``allauth.account.signals.user_signed_up(request, user)``
    Sent when a user signs up for an account. This signal is
    typically followed by a ``user_logged_in``, unless email verification
    prohibits the user to log in.

- ``allauth.account.signals.password_set(request, user)``
    Sent when a password has been successfully set for the first time.

- ``allauth.account.signals.password_changed(request, user)``
    Sent when a password has been successfully changed.

- ``allauth.account.signals.password_reset(request, user)``
    Sent when a password has been successfully reset.

- ``allauth.account.signals.email_confirmed(request, email_address)``
    Sent after the email address in the db was updated and set to confirmed.

- ``allauth.account.signals.email_confirmation_sent(request, confirmation, signup)``
    Sent right after the email confirmation is sent.

- ``allauth.account.signals.email_changed(request, user, from_email_address, to_email_address)``
    Sent when a primary email address has been changed.

- ``allauth.account.signals.email_added(request, user, email_address)``
    Sent when a new email address has been added.

- ``allauth.account.signals.email_removed(request, user, email_address)``
    Sent when an email address has been deleted.
