ORCID
-----

The ORCID provider should work out of the box provided that you are using the
Production ORCID registry and the public API. In other settings, you will need
to define the API you are using in your site's settings, as follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'orcid': {
            # Base domain of the API. Default value: 'orcid.org', for the production API
            'BASE_DOMAIN':'sandbox.orcid.org',  # for the sandbox API
            # Member API or Public API? Default: False (for the public API)
            'MEMBER_API': True,  # for the member API
        }
    }
