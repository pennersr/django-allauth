VK
--

App registration
    https://vk.com/editapp?act=create

Development callback URL ("Site address")
    http://localhost
    https://localhost

    Note: You have to use ports 80 or 443 to test VK locally, VK doesn't
    support other ports for now


Django configuration
********************

Use the following settings example to login via VK (full name - VK ID).

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'vk': {
            "APPS": [
                {
                    "client_id": "YOUR_CLIENT_ID",
                    "secret": "YOUR_CLIENT_SECRET",
                    "key": "",
                },
            ],
            'SCOPE': [
                'email',
            ],
        }
    }


Don't forget to add VK provider into Django installed apps:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'allauth.socialaccount.providers.vk',
        ...
    ]
