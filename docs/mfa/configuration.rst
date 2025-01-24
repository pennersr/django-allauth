Configuration
=============

Available settings:

``MFA_ADAPTER`` (default: ``"allauth.mfa.adapter.DefaultMFAAdapter"``)
  Specifies the adapter class to use, allowing you to alter certain
  default behavior.

``MFA_FORMS``
  Used to override forms. Defaults to::

    MFA_FORMS = {
        'authenticate': 'allauth.mfa.base.forms.AuthenticateForm',
        'reauthenticate': 'allauth.mfa.base.forms.AuthenticateForm',
        'activate_totp': 'allauth.mfa.totp.forms.ActivateTOTPForm',
        'deactivate_totp': 'allauth.mfa.totp.forms.DeactivateTOTPForm',
        'generate_recovery_codes': 'allauth.mfa.recovery_codes.forms.GenerateRecoveryCodesForm',
    }

``MFA_PASSKEY_LOGIN_ENABLED`` (default: ``False``)
  Whether or not end users can login using a (WebAuthn) passkey. Note that for
  this to be enabled, you also need to add ``"webauthn"`` to
  ``MFA_SUPPORTED_TYPES``.

``MFA_PASSKEY_SIGNUP_ENABLED`` (default: ``False``)
  Whether or not end users can signup using a (WebAuthn) passkey. Note that for
  this to be enabled, you need to add ``"webauthn"`` to ``MFA_SUPPORTED_TYPES``,
  require mandatory email verification and have
  ``ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED`` set to ``True``.

``MFA_RECOVERY_CODE_COUNT`` (default: ``10``)
  The number of recovery codes.

``MFA_RECOVERY_CODE_DIGITS`` (default: ``8``)
  The number of digits of each recovery code.

``MFA_SUPPORTED_TYPES`` (default: ``[["recovery_codes", "totp"]``)
  The authenticator types that end users are able to setup. Allowed
  types are: ``"recovery_codes"``, ``"totp"``, and ``"webauthn"``. The
  latter is disabled by default.

``MFA_TOTP_PERIOD`` (default: ``30``)
  The period that a TOTP code will be valid for, in seconds.

``MFA_TOTP_TOLERANCE`` (default: ``0``)
  The number of time steps in the past or future to allow. Lower values are more secure, but more likely to fail due to clock drift.

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
