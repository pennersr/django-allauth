Signals
=======

There are several signals emitted during MFA flows. You can
hook to them for your own needs.

- ``allauth.mfa.signals.authenticator_added(request, user, authenticator)``
    Sent when an authenticator is added.

- ``allauth.mfa.signals.authenticator_removed(request, user, authenticator)``
    Sent when an authenticator is removed.

- ``allauth.mfa.signals.authenticator_reset(request, user, authenticator)``
    Sent when an authenticator is reset (e.g. recovery codes regenerated).

- ``allauth.mfa.signals.authenticator_used(request, user, authenticator, reauthenticated, passwordless)``
    Sent when an authenticator is successfully used, e.g. for login or
    reauthentication purposes.

- ``allauth.mfa.signals.authentication_failed(request, user, authenticator, reauthentication)``
    Sent when authentication via MFA failed, e.g. when an incorrect code was
    entered.
