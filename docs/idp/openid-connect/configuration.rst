Configuration
=============

Available settings:

``IDP_OIDC_ACCESS_TOKEN_EXPIRES_IN`` (default: 3600)
  The time (in seconds) after which access tokens expire.

``IDP_OIDC_ADAPTER`` (default: ``"allauth.idp.oidc.adapter.DefaultOIDCAdapter"``)
  Specifies the adapter class to use, allowing you to alter certain
  default behavior.

``IDP_OIDC_AUTHORIZATION_CODE_EXPIRES_IN`` (default: 60)
  The time (in seconds) after which authorization codes expire.

``IDP_OIDC_DEVICE_CODE_EXPIRES_IN`` (default: 300)
  The time (in seconds) after which device codes expire.

``IDP_OIDC_DEVICE_CODE_INTERVAL`` (default: 5)
  The time (in seconds) a client should wait between polling attempts when using
  the device authorization flow.

``IDP_OIDC_ID_TOKEN_EXPIRES_IN`` (default: 300)
  The time (in seconds) after which ID tokens expire.

``IDP_OIDC_PRIVATE_KEY`` (default: ``""``)
  The private key used for creating ID tokens (and ``.well-known/jwks.json``).

``IDP_OIDC_RATE_LIMITS`` (default: ``{"device_user_code": "5/m/ip"}``)
  Rate limit configuration.

``IDP_OIDC_ROTATE_REFRESH_TOKEN`` (default: ``True``)
  When access tokens are refreshed the old refresh token can be kept
  (``False``) or replaced (``True``) with a new one (rotated).
