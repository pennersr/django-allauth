Configuration
=============

Available settings:

``HEADLESS_ADAPTER`` (default: ``"allauth.headless.adapter.DefaultHeadlessAdapter"``)
  Specifies the adapter class to use, allowing you to alter certain
  default behavior.

``HEADLESS_CLIENTS`` (default: ``("app", "browser")``)
  Specifies the supported types of clients for the API. Setting this to
  e.g. ``("app",)`` will remove all ``"browser"`` related endpoints.

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
        "account_reset_password": "https://app.project.org/account/password/reset",
        "account_reset_password_from_key": "https://app.project.org/account/password/reset/key/{key}",
        "account_signup": "https://app.project.org/account/signup",
        # Fallback in case the state containing the `next` URL is lost and the handshake
        # with the third-party provider fails.
        "socialaccount_login_error": "https://app.project.org/account/provider/callback",
    }

``HEADLESS_ONLY`` (default: ``False``)
  You can use headless-only mode in case your application fully takes care of
  the frontend, and you do not want for e.g. the login and signup views to be
  accessible. In this case, including ``allauth.urls`` skips those views, yet,
  still includes e.g. the provider callback views.

``HEADLESS_SERVE_SPECIFICATION`` (default: ``False``)
  Whether or not to serve the OpenAPI specification files. When enabled, the
  endpoints ``/_allauth/openapi.yaml``, ``/_allauth/openapi.json`` and
  ``/_allauth/docs`` become available.

``HEADLESS_SPECIFICATION_TEMPLATE_NAME`` (default: ``"headless/spec/redoc_cdn.html"``)
  The template used to serve the OpenAPI specification in HTML format. Out of the box,
  Redoc (``"headless/spec/redoc_cdn.html"``) and Swagger (
  (``"headless/spec/swagger_cdn.html"``) are available.

``HEADLESS_TOKEN_STRATEGY`` (default: ``"allauth.headless.tokens.sessions.SessionTokenStrategy"``)
  If you need to change the way tokens are created and handled, you can plug in your own
  :doc:`./tokens`.
