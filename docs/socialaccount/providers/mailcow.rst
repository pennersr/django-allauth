Mailcow
-------

To register the app with Mailcow, follow the applicable sections of the guide
for Nextcloud authentication in the Mailcow documentation::

   https://docs.mailcow.email/third_party/nextcloud/third_party-nextcloud/

The scope ``profile`` is used automatically and not configurable.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        "mailcow": {
            # Server to which to authenticate. Default value: https://hosted.mailcow.de
            "SERVER": "https://<mailcow-hostname>",
            # Definition of the app with the client ID and secret configured in Mailcow
            "APP": {
                # ...
            }
        }
    }
