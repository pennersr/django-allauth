from typing import Any, Dict, Optional

from django import forms
from django.forms import widgets
from django.utils.translation import gettext as _

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.models import EmailAddress
from allauth.core import context
from allauth.core.internal import ratelimit
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.internal.clientkit import clean_post_logout_redirect_uri
from allauth.idp.oidc.internal.oauthlib import device_codes
from allauth.idp.oidc.internal.tokens import decode_jwt_token
from allauth.idp.oidc.models import Client


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


class RPInitiatedLogoutForm(forms.Form):
    """
    We don't throw validation errors in case of wrong inputs:

    > If any of the validation procedures defined in this specification fail,
    > any operations requiring the information that failed to correctly validate
    > MUST be aborted and the information that failed to validate MUST NOT be
    > used.

    """

    action = forms.CharField(required=False, widget=forms.HiddenInput)

    # RECOMMENDED. ID Token previously issued by the OP to the RP passed to the
    # Logout Endpoint as a hint about the End-User's current authenticated
    # session with the Client. This is used as an indication of the identity of
    # the End-User that the RP is requesting be logged out by the OP.
    id_token_hint = forms.CharField(required=False, widget=forms.HiddenInput)

    # OPTIONAL. Hint to the Authorization Server about the End-User that is
    # logging out. The value and meaning of this parameter is left up to the
    # OP's discretion. For instance, the value might contain an email address,
    # phone number, username, or session identifier pertaining to the RP's
    # session with the OP for the End-User.
    logout_hint = forms.CharField(required=False, widget=forms.HiddenInput)

    # OPTIONAL. OAuth 2.0 Client Identifier valid at the Authorization
    # Server. When both client_id and id_token_hint are present, the OP MUST
    # verify that the Client Identifier matches the one used when issuing the ID
    # Token. The most common use case for this parameter is to specify the
    # Client Identifier when post_logout_redirect_uri is used but id_token_hint
    # is not. Another use is for symmetrically encrypted ID Tokens used as
    # id_token_hint values that require the Client Identifier to be specified by
    # other means, so that the ID Tokens can be decrypted by the OP.
    client_id = forms.CharField(required=False, widget=forms.HiddenInput)

    # OPTIONAL. URI to which the RP is requesting that the End-User's User Agent
    # be redirected after a logout has been performed.
    post_logout_redirect_uri = forms.URLField(required=False, widget=forms.HiddenInput)

    # OPTIONAL. Opaque value used by the RP to maintain state between the logout
    # request and the callback to the endpoint specified by the
    # post_logout_redirect_uri parameter. If included in the logout request, the
    # OP passes this value back to the RP using the state parameter when
    # redirecting the User Agent back to the RP.
    state = forms.CharField(required=False, widget=forms.HiddenInput)

    # End-User's preferred languages and scripts for the user interface,
    # represented as a space-separated list of BCP47 [RFC5646] language tag
    # values, ordered by preference. For instance, the value "fr-CA fr en"
    # represents a preference for French as spoken in Canada, then French
    # (without a region designation), followed by English (without a region
    # designation). An error SHOULD NOT result if some or all of the requested
    # locales are not supported by the OpenID Provider.
    ui_locales = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_id_token_hint(self):
        value = self.cleaned_data["id_token_hint"]
        if not value:
            return None
        payload = decode_jwt_token(value, verify_exp=False, verify_iss=True)
        return payload

    def clean(self) -> Optional[Dict[str, Any]]:
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data
        post_logout_redirect_uri = cleaned_data.get("post_logout_redirect_uri")

        client: Optional[Client] = None
        client_id = cleaned_data.get("client_id")
        id_token_hint = cleaned_data.get("id_token_hint")
        aud: Optional[str] = None
        if id_token_hint:
            aud = id_token_hint.get("aud")
            if aud and client_id and aud != client_id:
                # aud doesn't match client_id, don't trust any of these.
                id_token_hint = cleaned_data["id_token_hint"] = None
                client_id = cleaned_data["client_id"] = None
                aud = None
            elif aud and not client_id:
                client_id = aud

        if client_id:
            client = Client.objects.filter(id=client_id).first()
            if not client:
                # Wipe invalid inputs.
                client_id = cleaned_data["client_id"] = None
                if aud:
                    id_token_hint = cleaned_data["id_token_hint"] = None

        cleaned_data["post_logout_redirect_uri"] = clean_post_logout_redirect_uri(
            post_logout_redirect_uri, client
        )
        cleaned_data["client"] = client
        return cleaned_data
