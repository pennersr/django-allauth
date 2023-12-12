Configuration
=============

Available settings:

``MFA_ADAPTER`` (default: ``"allauth.mfa.adapter.DefaultMFAAdapter"``)
  Specifies the adapter class to use, allowing you to alter certain
  default behaviour.

``MFA_FORMS``
  Used to override forms. Defaults to::

    MFA_FORMS = {
        'authenticate': 'allauth.mfa.forms.AuthenticateForm',
        'reauthenticate': 'allauth.mfa.forms.AuthenticateForm',
        'activate_totp': 'allauth.mfa.forms.ActivateTOTPForm',
        'deactivate_totp': 'allauth.mfa.forms.DeactivateTOTPForm',
    }

``MFA_RECOVERY_CODE_COUNT`` (default: ``10``)
  The number of recovery codes.

``MFA_TOTP_PERIOD`` (default: ``30``)
  The period that a TOTP code will be valid for, in seconds.

``MFA_TOTP_DIGITS`` (default: ``6``)
  The number of digits for TOTP codes.

``MFA_TOTP_ISSUER`` (default: ``""``)
  The issuer (appearing in the TOTP QR code).
