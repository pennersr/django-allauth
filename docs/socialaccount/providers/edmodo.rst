Edmodo
------

Edmodo OAuth2 documentation
    https://developers.edmodo.com/edmodo-connect/edmodo-connect-overview-getting-started/

You can optionally specify additional permissions to use. If no ``SCOPE``
value is set, the Edmodo provider will use ``basic`` by default:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'edmodo': {
            'SCOPE': [
                'basic',
                'read_groups',
                'read_connections',
                'read_user_email',
                'create_messages',
                'write_library_items',
            ]
        }
    }
