Configuration
=============

Available settings:

``ALLAUTH_DEFAULT_AUTO_FIELD``
  Can be set to configure the primary key of all models. For
  example: ``"hashid_field.HashidAutoField"``.

``ALLAUTH_USER_CODE_FORMAT`` (default: ``{"numeric": False, "dashed": True, length: 8}``)
  Controls the format of user-facing verification codes (e.g. email
  verification, phone verification, login codes).
