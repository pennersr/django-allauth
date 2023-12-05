Configuration
=============

Available settings:

``USERSESSIONS_ADAPTER`` (default: ``"allauth.usersessions.adapter.DefaultUserSessionsAdapter"``)
  Specifies the adapter class to use, allowing you to alter certain
  default behaviour.

``USERSESSIONS_TRACK_ACTIVITY`` (default: ``False``)
  Whether or not user sessions are kept updated. User sessions are created at
  login time, but as the user continues to access the site the IP address might
  change. Enabling this setting makes sure that the session is kept track of,
  meaning, the IP address, user agent and last seen timestamp are all kept up to
  date. Requires ``allauth.usersessions.middleware.UserSessionsMiddleware`` to
  be installed.
