Installation
============

In order to use this functionality you need to install the
``idp-oidc`` extra as follows::

  pip install "django-allauth[idp-oidc]"

As the provider functionality is dependent on the regular allauth account
handling, you will need to follow the installation instructions related to
``allauth.account`` first. On top of that, you will need to add the following to
your project setup.

In your ``settings.py``, include the OpenID Connect provider app::

    INSTALLED_APPS = [
        ...
        "allauth.idp.oidc",
        ...
    ]

Next, create a private key using the following command::

    openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048

Then, include that ``private_key.pem`` in your ``settings.py``::

    IDP_OIDC_PRIVATE_KEY = """
    -----BEGIN PRIVATE KEY-----
    MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCiStSwvoSk61uf
    cQvkGDmR6gsM2QjVgKxCTPtg3tMhMO7kXq3PPMEiWlF49JicjPWs5vkYcLAsWNVE
    ...
    rfnteLIERvzd4rLi9WjTahfKA2Mq3YNIe3Hw8IDrrczJgd/XkEaENGYXmmNCX22B
    gtUcukumVPtrDhGK9i/PG3Q=
    -----END PRIVATE KEY-----
    """

Your project ``urls.py`` should include::

    urlpatterns = [
        ...
        path("", include("allauth.idp.urls")),
        ...
    ]
