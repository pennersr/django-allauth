URLs & Views
============

Your project ``urls.py`` should include:

.. code-block:: python

    urlpatterns = [
        ...
        path("", include("allauth.idp.urls")),
        ...
    ]

The above will enable the following views:

``/.well-known/openid-configuration``
  Provides the OpenID Provider Configuration Information. This endpoint returns
  a JSON document that includes metadata about the OIDC provider, such as
  supported authentication methods, token endpoints, and available scopes.

``/.well-known/jwks.json``
  Serves the JSON Web Key Set (JWKS) used to verify the signatures of JWTs
  issued by the OIDC provider. Clients use this to validate ID tokens and access
  tokens.

``/identity/o/authorize``
  The authorization endpoint used to initiate the OAuth2/OIDC flow. It handles
  authentication requests and issues authorization codes or tokens based on the
  request parameters.

``/identity/o/api/revoke``
  Allows clients to revoke access or refresh tokens. This endpoint helps
  maintain security by invalidating credentials that are no longer needed or
  have been compromised.

``/identity/o/api/userinfo``
  Returns user profile information in a JSON format. This endpoint is typically
  used after a successful authentication to fetch claims about the authenticated
  user.

``/identity/o/api/token``
  Handles the exchange of authorization codes for tokens, or client credentials
  for access tokens. This is a key component of the token flow in OAuth2/OIDC.
