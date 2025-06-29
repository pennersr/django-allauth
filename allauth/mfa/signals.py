from django.dispatch import Signal

from allauth.account import app_settings as account_settings
from allauth.mfa import app_settings
from allauth.mfa.adapter import get_adapter
from allauth.mfa.utils import is_mfa_enabled


# Emitted when an authenticator is added.
# Arguments: request, user, authenticator
authenticator_added = Signal()

# Emitted when an authenticator is removed.
# Arguments: request, user, authenticator
authenticator_removed = Signal()

# Emitted when an authenticator is reset (e.g. recovery codes regenerated).
# Arguments: request, user, authenticator
authenticator_reset = Signal()


def on_add_email(sender, email, user, **kwargs):
    if app_settings.ALLOW_UNVERIFIED_EMAIL:
        return
    if account_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
        return
    if is_mfa_enabled(user):
        adapter = get_adapter()
        raise adapter.validation_error("add_email_blocked")
