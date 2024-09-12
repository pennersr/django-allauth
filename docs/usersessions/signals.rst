Signals
=======

The following signal is emitted while handling user sessiond.

- ``allauth.usersessions.signals.session_client_changed(request, from_session, to_session)``
    This signal is emitted when the IP or user agent changes during the lifetime of a user
    session. Note that it only fires when ``USERSESSIONS_TRACK_ACTIVITY`` is turned on.
