Installation
============

In your ``settings.py``, include::

  INSTALLED_APPS = [
      ...

      # Required
      'allauth.account',
      'allauth.headless',

      # Optional
      'allauth.socialaccount',
      'allauth.mfa',
      'allauth.usersessions',

      ...
  ]

  # These are the URLs to be implemented by your single-page application.
  HEADLESS_FRONTEND_URLS = {
      "account_confirm_email": "https://app.project.org/account/verify-email/{key}",
      "account_reset_password_from_key": "https://app.org/account/password/reset/key/{key}",
      "account_signup": "https://app.org/account/signup",
  }


Your project ``urls.py`` should include::

    urlpatterns = [
        # Even when using headless, the third-party provider endpoints are stil
        # needed for handling e.g. the OAuth handshake. The account views
        # can be disabled using `HEADLESS_ONLY = True`.
        path("accounts/", include("allauth.urls")),

        # Include the API endpoints:
        path("_allauth/", include("allauth.headless.urls")),
    ]
