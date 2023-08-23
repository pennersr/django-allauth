DingTalk
--------

The DingTalk OAuth2 documentation:

    https://open.dingtalk.com/document/orgapp-server/obtain-identity-credentials

You can optionally specify additional scope to use. If no ``SCOPE`` value
is set, will use ``openapi`` by default(for Open Platform Account, need
registration). Other ``SCOPE`` options are: corpid.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'dingtalk': {
            'APP': {
                'client_id': 'xxxx',
                'secret': 'xxxx',
           },
    }
    }
