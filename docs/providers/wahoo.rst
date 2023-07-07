Wahoo
-----

Register your OAuth2 app here:

    https://developers.wahooligan.com/applications/new

The API documentation can be found here:

    https://cloud-api.wahooligan.com/#introduction

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'wahoo': {
            'SCOPE': ['user_read'],
        }
    }

SCOPE:
    The default scope is ``user_read`` which allows you to read profile data. If
    ``SOCIALACCOUNT_QUERY_EMAIL`` is set to True the ``email`` scope is also requested.

    In order to read or write workout history data you must request additional scopes.

    The available scopes are: ``user_read``, ``user_write``, ``workouts_read``, ``workouts_write``,
    ``offline_data``.
