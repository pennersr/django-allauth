from django import forms
from django.forms import widgets
from django.utils.translation import gettext as _

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.models import EmailAddress
from allauth.core import context
from allauth.core.internal import ratelimit
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.internal.oauthlib import device_codes


class AuthorizationForm(forms.Form):
    request = forms.CharField(widget=widgets.HiddenInput)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        requested_scopes = kwargs.pop("requested_scopes")
        super().__init__(*args, **kwargs)
        adapter = get_adapter()
        choices = [(rs, adapter.scope_display.get(rs, rs)) for rs in requested_scopes]
        choices = sorted(choices, key=lambda ch: ch[1])
        self.fields["scopes"] = forms.MultipleChoiceField(
            choices=choices,
            label=_("Grant permissions"),
            widget=forms.CheckboxSelectMultiple,
            initial=requested_scopes,
            required=True,
        )
        emails = list(
            EmailAddress.objects.filter(user=user, verified=True)
            .order_by("-primary", "email")
            .values_list("email", flat=True)
        )
        if "email" in requested_scopes and len(emails) > 1:
            self.fields["email"] = forms.ChoiceField(
                label=_("Email"),
                choices=[(email, email) for email in emails],
                required=False,
            )


class ConfirmCodeForm(forms.Form):
    code = forms.CharField(
        label=_("Code"),
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": _("Code"), "autocomplete": "one-time-code"},
        ),
    )

    def __init__(self, *args, **kwargs):
        self.code = kwargs.pop("code", None)
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if not ratelimit.consume(
            context.request,
            action="device_user_code",
            config=app_settings.RATE_LIMITS,
            limit_get=True,
        ):
            raise get_account_adapter().validation_error("rate_limited")

        self.device_code, self.client = device_codes.validate_user_code(code)
        return code


class DeviceAuthorizationForm(forms.Form):
    action = forms.CharField(required=False)
