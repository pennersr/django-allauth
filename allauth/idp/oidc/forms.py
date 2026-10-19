from __future__ import annotations

from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.translation import gettext as _

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.models import EmailAddress
from allauth.core import context
from allauth.core.internal import ratelimit
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.internal.clientkit import (
    clean_post_logout_redirect_uri,
    lookup_client,
)
from allauth.idp.oidc.internal.oauthlib import device_codes
from allauth.idp.oidc.internal.tokens import decode_jwt_token
from allauth.idp.oidc.models import Client


class AuthorizationForm(forms.Form):
    request = forms.CharField(widget=widgets.HiddenInput)

    def __init__(self, *args, **kwargs) -> None:
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

    def __init__(self, *args, **kwargs) -> None:
        self.code = kwargs.pop("code", None)
        super().__init__(*args, **kwargs)

    def clean_code(self) -> str:
        code = self.cleaned_data["code"]
        if not ratelimit.consume(
            context.request,
            action="device_user_code",
            app="allauth.idp.oidc",
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
    post_logout_redirect_uri = forms.CharField(required=False, widget=forms.HiddenInput)

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

    def clean_id_token_hint(self) -> dict | None:
        value = self.cleaned_data["id_token_hint"]
        if not value:
            return None
        payload = decode_jwt_token(value, verify_exp=False, verify_iss=True)
        return payload

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data
        post_logout_redirect_uri = cleaned_data.get("post_logout_redirect_uri")

        client: Client | None = None
        client_id = cleaned_data.get("client_id")
        id_token_hint = cleaned_data.get("id_token_hint")
        aud: str | None = None
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
            client = lookup_client(client_id)
            if not client:
                # Wipe invalid inputs.
                client_id = cleaned_data["client_id"] = None
                if aud:
                    id_token_hint = cleaned_data["id_token_hint"] = None

        try:
            cleaned_data["post_logout_redirect_uri"] = clean_post_logout_redirect_uri(
                post_logout_redirect_uri, client
            )
        except ValidationError as e:
            self.add_error("post_logout_redirect_uri", e)
        cleaned_data["client"] = client
        return cleaned_data


class ClientRegistrationForm(forms.Form):
    client_name = Client._meta.get_field("name").formfield(required=False)
    redirect_uris = forms.JSONField(required=True)
    post_logout_redirect_uris = forms.JSONField(required=False)
    grant_types = forms.JSONField(required=False)
    response_types = forms.JSONField(required=False)
    token_endpoint_auth_method = forms.CharField(required=False)
    scope = forms.CharField(required=False)

    def clean_client_name(self) -> str:
        value = self.cleaned_data.get("client_name") or ""
        if "<" in value or ">" in value:
            raise forms.ValidationError("Client name must not contain '<' or '>'.")
        return value.strip()

    def _clean_string_list(self, field_name: str) -> list[str]:
        value = self.cleaned_data.get(field_name)
        if value is None:
            return []
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise forms.ValidationError(f"{field_name} must be an array of strings.")
        return value

    def clean_redirect_uris(self) -> list[str]:
        uris = self._clean_string_list("redirect_uris")
        if not uris:
            raise forms.ValidationError(
                "redirect_uris is required and must be a non-empty array."
            )
        return uris

    def clean_post_logout_redirect_uris(self) -> list[str]:
        return self._clean_string_list("post_logout_redirect_uris")

    def clean_grant_types(self) -> list[str]:
        grant_types = self._clean_string_list("grant_types") or ["authorization_code"]
        valid = {gt.value for gt in Client.GrantType}
        invalid = set(grant_types) - valid
        if invalid:
            raise forms.ValidationError(
                f"Unsupported grant type(s): {', '.join(sorted(invalid))}"
            )
        return grant_types

    def clean_response_types(self) -> list[str]:
        response_types = self._clean_string_list("response_types") or ["code"]
        valid = {rt.value for rt in Client.ResponseType}
        invalid = set(response_types) - valid
        if invalid:
            raise forms.ValidationError(
                f"Unsupported response type(s): {', '.join(sorted(invalid))}"
            )
        return response_types

    def clean_scope(self) -> list[str]:
        value = self.cleaned_data.get("scope", "")
        if isinstance(value, str):
            scopes = value.split()
        elif isinstance(value, (list, tuple)):
            scopes = [str(s).strip() for s in value]
        else:
            scopes = []
        return scopes or ["openid"]

    def clean_token_endpoint_auth_method(self) -> str:
        # If unspecified or omitted, the default is "client_secret_basic",
        # denoting the HTTP Basic authentication scheme as specified in Section
        # 2.3.1 of OAuth 2.0
        value = (
            self.cleaned_data.get("token_endpoint_auth_method")
            or Client.AuthenticationMethod.CLIENT_SECRET_BASIC
        )
        valid = {am.value for am in Client.AuthenticationMethod}
        if value not in valid:
            raise forms.ValidationError(
                f"Unsupported token endpoint auth method: {value}"
            )
        return value

    def save(self, commit: bool = True) -> Client:
        data = self.cleaned_data
        kwargs = {
            "name": data["client_name"],
            "type": (
                Client.Type.PUBLIC
                if data["token_endpoint_auth_method"]
                == Client.AuthenticationMethod.NONE
                else Client.Type.CONFIDENTIAL
            ),
        }
        client = Client(**kwargs)
        client.set_grant_types(data["grant_types"])
        client.set_response_types(data["response_types"])
        client.set_scopes(data["scope"])
        client.set_redirect_uris(data["redirect_uris"])
        if commit:
            client.save()
        return client
