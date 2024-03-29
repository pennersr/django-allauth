from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from allauth import app_settings
from allauth.account.adapter import get_adapter
from allauth.mfa.utils import is_mfa_enabled


class RequireMFAMiddleware(MiddlewareMixin):
    """Force multi-factor authentication for certain users."""

    allowed_urls = [
        "account_login",
        "account_change_password",
        "account_logout",
        "account_reset_password",
        "mfa_activate_totp",
    ]

    def mfa_required(self, request):
        """
        Check whether this request requires MFA.

        Should return True if MFA is required, else False.
        """
        raise NotImplementedError("Subclasses must implement mfa_required()")

    def redirect_to_mfa_setup(self, request):
        adapter = get_adapter(request)
        adapter.add_message(request, messages.ERROR, "mfa/messages/require_mfa.txt")
        return HttpResponseRedirect(reverse("mfa_activate_totp"))

    def process_view(self, request, view_func, view_args, view_kwargs):
        # If MFA is not enabled, do nothing
        if not app_settings.MFA_ENABLED:
            return None

        # If the user is not authenticated, do nothing
        if not request.user.is_authenticated:
            return None

        # If we are on an allowed page, do nothing
        if request.resolver_match.url_name in self.allowed_urls:
            return None

        # If this request does not require MFA, do nothing
        if not self.mfa_required(request):
            return None

        # If the user has MFA enabled already, do nothing
        if is_mfa_enabled(request.user):
            return None

        return self.redirect_to_mfa_setup(request)
