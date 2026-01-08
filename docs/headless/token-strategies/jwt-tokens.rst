JWT Tokens
==========

Introduction
------------

When using the JWT token strategy, an access token and refresh token pair is
handed out when the user becomes fully authenticated. The access token is a JWT
token, and is typically short-lived. The refresh token can be used to issue a
new access token in case the access token is expired.

The use of JWT is mainly beneficial for a multi-service architecture, where
authentication can be performed in each service without having to contact a
central authority.

Often, the JWT token strategy is incorrectly touted as being stateless. Unless
it is acceptable that access tokens can still be used after logging out, state
is needed to invalidate outstanding access tokens, diminishing the stateless
aspect of the JWT token strategy.


Usage
-----

With the JWT token strategy enabled, the way of working is as follows:

- End users are guided through the authentication process. For as long as
  they are not fully authenticated, you communicate the ``X-Session-Token`` header
  back to the allauth API.

- In the response of the request that resulted in the user becoming fully
  authenticated, you will find an access token and refresh token pair in the
  ``meta`` payload.

- From this moment onward, your application can drop the ``X-Session-Token``
  completely.  The access token can be used to reach out to your own API
  endpoints, as well as to the allauth API endpoints.


Configuration
-------------

Available settings:

``HEADLESS_JWT_ALGORITHM`` (default: ``"RS256"``)
  The algorithm used to sign the tokens. For asymmetric algorithms (e.g. ``"RS256"``),
  the ``HEADLESS_JWT_PRIVATE_KEY`` is used as the RSA private key. For symmetric
  algorithms (e.g. ``"HS256"``), ``HEADLESS_JWT_PRIVATE_KEY`` is used as the
  secret. In case a symmetric algorithm is used and the private key is not
  configured, ``settings.SECRET_KEY`` is used as a fallback.

``HEADLESS_JWT_PRIVATE_KEY`` (default: ``""``)
  The private key (or secret) used to sign the JWT tokens. For asymmetric
  algorithms, it can be generated using the following command::

    openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048

  Then, include that ``private_key.pem`` in your ``settings.py``::

    HEADLESS_JWT_PRIVATE_KEY = """
    -----BEGIN PRIVATE KEY-----
    MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCiStSwvoSk61uf
    cQvkGDmR6gsM2QjVgKxCTPtg3tMhMO7kXq3PPMEiWlF49JicjPWs5vkYcLAsWNVE
    ...
    rfnteLIERvzd4rLi9WjTahfKA2Mq3YNIe3Hw8IDrrczJgd/XkEaENGYXmmNCX22B
    gtUcukumVPtrDhGK9i/PG3Q=
    -----END PRIVATE KEY-----
    """

``HEADLESS_JWT_ACCESS_TOKEN_EXPIRES_IN`` (default: ``300``)
  The lifetime (in seconds) of the access tokens.

``HEADLESS_JWT_REFRESH_TOKEN_EXPIRES_IN`` (default: ``86400``)
  The lifetime (in seconds) of the refresh tokens.

``HEADLESS_JWT_AUTHORIZATION_HEADER_SCHEME`` (default: ``"Bearer"``)
  Specifies the HTTP Authorization header scheme for access tokens, e.g.: ``Authorization: Bearer <access-token>``.

``HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED`` (default: ``False``)
  When enabled, it is validated that the access token still belongs to an
  active session. As a result, logging out will immediately invalidate the
  access token.

``HEADLESS_JWT_ROTATE_REFRESH_TOKEN`` (default: ``True``)
  When enabled, refreshing the access token results in a new refresh token
  as well. The original refresh token is invalidated.


Customization
-------------

You can customize the behavior of the JWT token strategy by creating a custom
class deriving from ``JWTTokenStrategy``, and pointing
``settings.HEADLESS_TOKEN_STRATEGY`` to that class.

.. autoclass:: allauth.headless.tokens.strategies.jwt.JWTTokenStrategy
   :members: get_claims


Securing Your API Endpoints
---------------------------

Django Ninja
~~~~~~~~~~~~

For Django Ninja, the following security class is available:

.. autoclass:: allauth.headless.contrib.ninja.security.JWTTokenAuth
   :members:

An example on how to use that security class in your own code is listed below:

.. code-block:: python

    from allauth.headless.contrib.ninja.security import jwt_token_auth
    from ninja import NinjaAPI

    api = NinjaAPI()

    @api.get("/your/own/api", auth=[jwt_token_auth])
    def your_own_api(request):
        ...



Django REST framework
~~~~~~~~~~~~~~~~~~~~~

For Django REST framework, the following authentication class is available:

.. autoclass:: allauth.headless.contrib.rest_framework.authentication.JWTTokenAuthentication
   :members:

An example on how to use that authentication class in your own code is listed below:

.. code-block:: python

    from allauth.headless.contrib.rest_framework.authentication import (
        JWTTokenAuthentication,
    )
    from rest_framework import permissions
    from rest_framework.views import APIView

    class YourOwnAPIView(APIView):

        authentication_classes = [
            JWTTokenAuthentication,
        ]
        permission_classes = [permissions.IsAuthenticated]

        def get(self, request):
            ...
