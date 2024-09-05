from functools import wraps

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.models import EmailAddress
from allauth.mfa.adapter import get_adapter


def validate_can_add_authenticator(user):
    """
    If we would allow users to enable 2FA with unverified email address,
    that would allow for an attacker to signup, not verify and prevent the real
    owner of the account from ever regaining access.
    """
    email_verified = not EmailAddress.objects.filter(user=user, verified=False).exists()
    if not email_verified:
        raise get_adapter().validation_error("unverified_email")


def redirect_if_add_not_allowed(function=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapper_view(request, *args, **kwargs):
            if request.user.is_authenticated:  # allow for this to go before reauth
                try:
                    validate_can_add_authenticator(request.user)
                except ValidationError as e:
                    for message in e.messages:
                        adapter = get_account_adapter()
                        adapter.add_message(request, messages.ERROR, message=message)
                    return HttpResponseRedirect(reverse("mfa_index"))
            return view_func(request, *args, **kwargs)

        return _wrapper_view

    if function:
        return decorator(function)
    return decorator
