Configuration
=============

Available settings:

``MFA_ADAPTER`` (default: ``"allauth.mfa.adapter.DefaultMFAAdapter"``)
  Specifies the adapter class to use, allowing you to alter certain
  default behavior.

``MFA_FORMS``
  Used to override forms. Defaults to::

    MFA_FORMS = {
        'authenticate': 'allauth.mfa.forms.AuthenticateForm',
        'reauthenticate': 'allauth.mfa.forms.AuthenticateForm',
        'activate_totp': 'allauth.mfa.forms.ActivateTOTPForm',
        'deactivate_totp': 'allauth.mfa.forms.DeactivateTOTPForm',
    }

``MFA_PASSKEY_LOGIN_ENABLED`` (default: ``False``)
  Whether or not end users can login using a (WebAuthn) passkey. Note that for
  this to be enabled, you also need to add ``"webauthn"`` to
  ``MFA_SUPPORTED_TYPES``.

``MFA_RECOVERY_CODE_COUNT`` (default: ``10``)
  The number of recovery codes.

``MFA_SUPPORTED_TYPES`` (default: ``[["recovery_codes", "totp"]``)
  The authenticator types that end users are able to setup. Allowed
  types are: ``"recovery_codes"``, ``"totp"``, and ``"webauthn"``. The
  latter is disabled by default.

``MFA_TOTP_PERIOD`` (default: ``30``)
  The period that a TOTP code will be valid for, in seconds.

``MFA_TOTP_DIGITS`` (default: ``6``)
  The number of digits for TOTP codes.

``MFA_TOTP_ISSUER`` (default: ``""``)
  The issuer (appearing in the TOTP QR code).

``MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN`` (default: ``False``)
  The WebAuthn uses the ``fido2`` package, and versions up to including version
  1.1.3 do not regard localhost as a secure origin, which is problematic during
  local development and testing. To work around that, you can use this setting.
  Only use this for development, never on production. See commit ``8b979313``
  over at ``fido2``.
