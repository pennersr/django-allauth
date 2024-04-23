Configuration
=============

Available settings:

``HEADLESS_ADAPTER`` (default: ``"allauth.headless.adapter.DefaultHeadlessAdapter"``)
  Specifies the adapter class to use, allowing you to alter certain
  default behaviour.

``HEADLESS_FRONTEND_URLS`` (default: ``{}``)
  Email confirmation and password reset mails contain links that by default point to the
  views from the ``allauth.account`` app. In case you  need to point these to your own frontend
  application, you can do so by configuring this setting, as follows::

    HEADLESS_FRONTEND_URLS = {
        "account_confirm_email": "https://app.project.org/account/verify-email/{key}",
        # Key placeholders are automatically populated. You are free to adjust this
        # to your own needs, e.g.
        #
        # "https://app.project.org/account/email/verify-email?token={key}",
        "account_reset_password_from_key": "https://app.project.org/account/password/reset/key/{key}",
        "account_signup_url": "https://app.project.org/account/signup",
    }

``HEADLESS_ONLY`` (default: ``False``)
  You can use headless-only mode in case your application fully takes care of
  the frontend, and you do not want for e.g. the login and signup views to be
  accessible. In this case, including ``allauth.urls`` skips those views, yet,
  still includes e.g. the provider callback views.

``HEADLESS_TOKEN_STRATEGY`` (default: ``"allauth.headless.tokens.sessions.SessionTokenStrategy"``)
  If you need to change the way tokens are created and handled, you can plug in your own
  :doc:`./tokens`.
