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
        }
    }

REST_API:
    Base URL of the MediaWiki site's REST API.
USERPAGE_TEMPLATE:
    Link template for linking to users. Must have a ``{username}`` format field.

With the default settings, Wikimedia user identities (meta.wikimedia.org) will be used.

App registration for Wikimedia wikis:
    https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose
