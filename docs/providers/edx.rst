Edx
------

Open Edx OAuth2 documentation
    https://course-catalog-api-guide.readthedocs.io/en/latest/authentication/

It is necessary to set ``EDX_URL`` to your open edx installation. If no ``EDX_URL``
value is set, the Edx provider will use ``https://edx.org`` which does not work:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
      'edx': {
          'EDX_URL': "https://openedx.local",
      }
    }
