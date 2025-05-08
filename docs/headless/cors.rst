Cross-Origin Resource Sharing (CORS)
====================================

In case your project requires CORS handling, the following configuration can be
used as a starting point:

.. code-block:: python

    MIDDLEWARE = (
        ...
        "corsheaders.middleware.CorsMiddleware",
        ...
    )

    INSTALLED_APPS = (
        ...
        "corsheaders",
        ...
    )

    CORS_ALLOWED_ORIGINS = [
        "https://app.project.org",
    ]

    from corsheaders.defaults import default_headers

    CORS_ALLOW_HEADERS = (
        *default_headers,
        "x-session-token",
        "x-email-verification-key",
        "x-password-reset-key",
    )
    CORS_ALLOW_CREDENTIALS = True
