Signals
=======

There are several signals emitted during authentication flows. You can
hook to them for your own needs.

- ``allauth.socialaccount.signals.pre_social_login(request, sociallogin)``
    Sent after a user successfully authenticates via a social provider,
    but before the login is fully processed. This signal is emitted as
    part of the social login and/or signup process, as well as when
    connecting additional social accounts to an existing account. Access
    tokens and profile information, if applicable for the provider, is
    provided.

- ``allauth.socialaccount.signals.social_account_added(request, sociallogin)``
    Sent after a user connects a social account to their local account. This
    is an explicit action and does not get called for the creation of a
    socialaccount.

- ``allauth.socialaccount.signals.social_account_updated(request, sociallogin)``
    Sent after a social account has been updated. This happens when a user
    logs in using an already connected social account, or completes a `connect`
    flow for an already connected social account. Useful if you need to
    unpack extra data for social accounts as they are updated.

- ``allauth.socialaccount.signals.social_account_removed(request, socialaccount)``
    Sent after a user disconnects a social account from their local
    account.
