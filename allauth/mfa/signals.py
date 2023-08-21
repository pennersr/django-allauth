from django.forms import ValidationError

from allauth.mfa.adapter import get_adapter
from allauth.mfa.utils import is_mfa_enabled


def on_add_email(sender, email, user, **kwargs):
    if is_mfa_enabled(user):
        adapter = get_adapter()
        raise ValidationError(adapter.error_messages["add_email_blocked"])
