Configuration
=============

Available settings:

``MFA_ADAPTER`` (default: ``"allauth.mfa.adapter.DefaultMFAAdapter"``)
  Specifies the adapter class to use, allowing you to alter certain
  default behavior.

``MFA_ALLOW_UNVERIFIED_EMAIL`` (default: ``False``)
  By default, an account that has an unverified email address is not allowed to
  turn on MFA. Additionally, accounts that have MFA turned on cannot add a new
  (unverified) email address. The rationale is that if this were allowed, it
  would allow an attacker to signup without verifying and then turn on MFA to
  prevent the real owner of the account from ever gaining access.  If the risk
  of this scenario is manageable for your project, you can allow unverified email
  address in combination with MFA by changing this setting.

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

``MFA_TRUST_ENABLED`` (default: ``False``)
  Enables the "Trust this browser?" functionality, which presents users with MFA
  enabled the choice to trust their browser allowing them to skip authenticating
  per MFA on each login. This is implemented by handing out a special trust
  cookie.

``MFA_TRUST_COOKIE_AGE`` (default: ``timedelta(days=14)``)
  Specifies the period (in seconds, or ``timedelta``) during which MFA is
  skipped.

``MFA_TRUST_COOKIE_NAME`` (default: ``"mfa_trusted"``)
  The name of the trust cookie.

``MFA_TRUST_COOKIE_DOMAIN`` (default: ``settings.SESSION_COOKIE_DOMAIN``)
  The domain of the trust cookie.

``MFA_TRUST_COOKIE_HTTPONLY`` (default: ``settings.SESSION_COOKIE_HTTPONLY``)
  Whether or not the trust cookie is HTTP only.

``MFA_TRUST_COOKIE_PATH`` (default: ``settings.SESSION_COOKIE_PATH``)
  The path set on the trust cookie.

``MFA_TRUST_COOKIE_SAMESITE`` (default: ``settings.SESSION_COOKIE_SAMESITE``)
  The value of the SameSite flag on the trust cookie.

``MFA_TRUST_COOKIE_SECURE`` (default: ``settings.SESSION_COOKIE_SECURE``)
  Whether to use a secure cookie for the trust cookie.
