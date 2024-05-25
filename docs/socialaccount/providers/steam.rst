Steam
-----

Steam is an OpenID-compliant provider. However, the `steam` provider allows
access to more of the user's details such as username, full name, avatar, etc.

Its implementation requires dependencies that are not installed by
default. Install using::

    $ pip install "django-allauth[socialaccount,steam]"

You need to register an API key here:
    https://steamcommunity.com/dev/apikey

Copy the Key supplied by the website above into BOTH Client ID and Secret
Key fields of the Social Application.
