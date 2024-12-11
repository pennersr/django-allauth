Provider Configuration
======================

Providers typically require various configuration parameters before your users
can authenticate with them. For example, for a regular OAuth provider you first
need to setup an OAuth app over on the provider developer portal. Then, you need
to configure the resulting client ID and client secret in your application.

Even though providers with other protocols may use different terminology, the
overall idea remains the same. Throughout allauth the term "social app" ("app"
for short) refers to the unit of configuration of a provider. You provide the
app configuration either in your project ``settings.py``, or, by means of
setting up ``SocialApp`` instances via the Django admin. When picking a method,
consider the following:

- Using the Django admin to setup ``SocialApp`` instances effectively stores
  secrets in your database, which has security implications.

- The ``SocialApp`` approach has (optional) support for the Django sites
  (``django.contrib.sites``). For example, it allows you to setup multiple apps
  for one and the same provider, and assign an app to a specific
  site/domain. This may be of use in a multi tenant setup.

**Important**: While you can mix both methods, be aware you need to avoid
configuring one and the same provider both via ``settings.py`` and a
``SocialApp`` instance.  In that case, it is not clear what app to pick,
resulting in a ``MultipleObjectsReturned`` exception.

The examples presented in this documentation are all settings based. If you
prefer the ``SocialApp`` based approach, simply create an entry via the Django
admin and populate the fields exactly like listed in the example.

The ``SOCIALACCOUNT_PROVIDERS`` setting is used to configure providers and their
apps. Next to the secrets that are configured per app, there are also parameters
such as ``VERIFIED_EMAIL`` that hold for all apps. The following is an example
configuration::

    SOCIALACCOUNT_PROVIDERS = {
        "github": {
            # For each provider, you can choose whether or not the
            # email address(es) retrieved from the provider are to be
            # interpreted as verified.
            "VERIFIED_EMAIL": True
        },
        "google": {
            # For each OAuth based provider, either add a ``SocialApp``
            # (``socialaccount`` app) containing the required client
            # credentials, or list them here:
            "APPS": [
                {
                    "client_id": "123",
                    "secret": "456",
                    "key": "",
                    "settings": {
                        # You can fine tune these settings per app:
                        "scope": [
                            "profile",
                            "email",
                        ],
                        "auth_params": {
                            "access_type": "online",
                        },
                    },
                },
            ],
            # The following provider-specific settings will be used for all apps:
            "SCOPE": [
                "profile",
                "email",
            ],
            "AUTH_PARAMS": {
                "access_type": "online",
            },
        }
    }

Note that provider-specific settings are documented `for each
provider separately <providers/index.html>`__.
