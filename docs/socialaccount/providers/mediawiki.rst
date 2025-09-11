MediaWiki
---------

MediaWiki OAuth2 documentation:
    https://www.mediawiki.org/wiki/OAuth/For_Developers

The following MediaWiki settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'mediawiki': {
            'REST_API': 'https://meta.wikimedia.org/w/rest.php',
            'USERPAGE_TEMPLATE': 'https://meta.wikimedia.org/wiki/{username}',
            # Identify your application with a descriptive user agent.
            # Format (generic template):
            #   <client>/<version> (<contact info>) [<extra lib>/<version> ...]
            # Contact info can be a user page URL, project URL, or email.
            # Example (bot):
            'USER_AGENT': 'CoolBot/1.2 (+https://example.org/coolbot/; operator@example.org) django-allauth',
        }
    }

REST_API:
    Base URL of the MediaWiki site's REST API.
USERPAGE_TEMPLATE:
    Link template for linking to users. Must have a ``{username}`` format field.
USER_AGENT:
    Custom User-Agent header sent with API requests. Wikimedia requires that
    automated clients send a descriptive User-Agent string with contact
    information. Generic defaults (e.g. ``python-requests/x``) or absent
    headers may be blocked or heavily rate limited. The recommended pattern is::

        <client>/<version> (<contact>) [<library>/<version> ...]

    where ``<contact>`` lets site operators reach you (URL or email). If you
    run a bot, consider including the word ``bot`` (any case) so traffic can be
    classified correctly. Do not spoof browser user agents.

    If not set, a generic ``django-allauth`` value is used; you should override
    this for production.

With the default settings, Wikimedia user identities (meta.wikimedia.org) will be used.

App registration for Wikimedia wikis:
    https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose
