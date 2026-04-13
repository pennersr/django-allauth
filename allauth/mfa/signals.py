from __future__ import annotations

from django.contrib.auth.base_user import AbstractBaseUser
from django.dispatch import Signal

from allauth.account import app_settings as account_settings
from allauth.mfa import app_settings
from allauth.mfa.adapter import get_adapter
from allauth.mfa.utils import is_mfa_enabled


# Emitted when an authenticator is added.
# Arguments:
# - request: HttpRequest
# - user: User
# - authenticator: Authenticator
authenticator_added = Signal()

# Emitted when an authenticator is removed.
# Arguments:
# - request: HttpRequest
# - user: User
# - authenticator: Authenticator
authenticator_removed = Signal()

# Emitted when an authenticator is reset (e.g. recovery codes regenerated).
# Arguments:
# - request: HttpRequest
# - user: User
# - authenticator: Authenticator
authenticator_reset = Signal()

# Emitted when an authenticator is successfully used (e.g. for login or reauthentication purposes).
# Arguments:
# - request: HttpRequest
# - user: User
# - authenticator: Authenticator
# - reauthenticated:bool
# - passwordless: bool
authenticator_used = Signal()

# Emitted when authentication via MFA failed, e.g. when an incorrect code was entered.
# Arguments:
# - request: HttpRequest
# - user: User
# - authenticator: Authenticator
# - reauthentication: bool (optional)
authentication_failed = Signal()


def on_add_email(sender, email, user: AbstractBaseUser, **kwargs) -> None:
    if app_settings.ALLOW_UNVERIFIED_EMAIL:
        return
    if account_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
        return
    if is_mfa_enabled(user):
        adapter = get_adapter()
        raise adapter.validation_error("add_email_blocked")
