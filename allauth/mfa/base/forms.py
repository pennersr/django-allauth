from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from allauth.core import context
from allauth.mfa import signals
from allauth.mfa.adapter import get_adapter
from allauth.mfa.base.internal.flows import check_rate_limit, post_authentication
from allauth.mfa.models import Authenticator


class BaseAuthenticateForm(forms.Form):
    code = forms.CharField(
        label=_("Code"),
        widget=forms.TextInput(
            attrs={"placeholder": _("Code"), "autocomplete": "one-time-code"},
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_code(self) -> str:
        clear_rl = check_rate_limit(self.user)
        code = self.cleaned_data["code"]
        main_auth: Authenticator | None = None
        for auth in Authenticator.objects.filter(user=self.user).exclude(
            # WebAuthn cannot validate manual codes.
            type=Authenticator.Type.WEBAUTHN
        ):
            if not main_auth or auth.type == Authenticator.Type.TOTP:
                # Don't emit failure signals to all authenticator, just to the
                # main one.
                main_auth = auth
            if auth.wrap().validate_code(code):
                auth.user = self.user
                self.authenticator = auth
                clear_rl()
                return code

        if main_auth:
            self._emit_authentication_failed(main_auth)
        raise get_adapter().validation_error("incorrect_code")

    def _emit_authentication_failed(self, authenticator: Authenticator) -> None:
        signals.authentication_failed.send(
            sender=Authenticator,
            request=context.request,
            user=self.user,
            authenticator=authenticator,
            reauthentication=False,
        )


class AuthenticateForm(BaseAuthenticateForm):
    def save(self) -> None:
        post_authentication(context.request, self.authenticator)


class ReauthenticateForm(BaseAuthenticateForm):
    def save(self) -> None:
        post_authentication(context.request, self.authenticator, reauthenticated=True)

    def _emit_authentication_failed(self, authenticator: Authenticator) -> None:
        signals.authentication_failed.send(
            sender=Authenticator,
            request=context.request,
            user=self.user,
            authenticator=authenticator,
            reauthentication=True,
        )
