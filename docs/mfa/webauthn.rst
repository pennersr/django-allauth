WebAuthn
========

WebAuthn support is disabled by default. To enable it, add these settings::

    # Make sure "webauthn" is included.
    MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]

    # Optional: enable support for logging in using a (WebAuthn) passkey.
    MFA_PASSKEY_LOGIN_ENABLED = True

    # Optional -- use for local development only: the WebAuthn uses the
    #``fido2`` package, and versions up to including version 1.1.3 do not
    # regard localhost as a secure origin, which is problematic during
    # local development and testing.
    MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = True

    # Add "humanize" contrib app if using default templates
    INSTALLED_APPS = [
        ...
        "django.contrib.humanize",
    ]
