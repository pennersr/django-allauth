ShareFile
---------

The following ShareFile settings are available.
  https://api.sharefile.com/rest/

SUBDOMAIN:
 Subdomain of your organization with ShareFile.  This is required.

 Example:
      ``test`` for ``https://test.sharefile.com``

APICP:
 Defaults to ``secure``.  Refer to the ShareFile documentation if you
 need to change this value.

DEFAULT_URL:
 Defaults to ``https://secure.sharefile.com``  Refer to the ShareFile
 documentation if you need to change this value.


Example:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
    'sharefile': {
        'SUBDOMAIN': 'TEST',
        'APICP': 'sharefile.com',
        'DEFAULT_URL': 'https://secure.sharefile.com',
                 }
    }
