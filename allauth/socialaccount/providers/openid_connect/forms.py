import requests

from django import forms

from allauth.socialaccount.internal import jwtkit
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.oauth2.client import OAuth2Error


BACKCHANNEL_LOGOUT_EVENT = "http://schemas.openid.net/event/backchannel-logout"


class BackchannelLogoutForm(forms.Form):
    logout_token = forms.CharField(
        error_messages={"required": "The logout_token parameter is required."}
    )

    def __init__(self, *args, adapter, provider, **kwargs):
        self.adapter = adapter
        self.provider = provider
        self.logout_data = None
        super().__init__(*args, **kwargs)

    def clean_logout_token(self):
        logout_token = self.cleaned_data["logout_token"]
        try:
            config = self.adapter.openid_config
            data = jwtkit.verify_and_decode(
                credential=logout_token,
                keys_url=config["jwks_uri"],
                issuer=config["issuer"],
                audience=self.provider.app.client_id,
                lookup_kid=jwtkit.lookup_kid_jwk,
            )
        except (
            KeyError,
            OAuth2Error,
            requests.RequestException,
            SocialApp.DoesNotExist,
        ) as exc:
            raise forms.ValidationError(
                "The logout token could not be validated."
            ) from exc

        events = data.get("events")
        if not (
            data.get("iss")
            and data.get("aud")
            and data.get("iat") is not None
            and data.get("exp") is not None
            and data.get("jti")
            and isinstance(events, dict)
            and BACKCHANNEL_LOGOUT_EVENT in events
            and isinstance(events[BACKCHANNEL_LOGOUT_EVENT], dict)
            # A Logout Token MUST contain either a sub or a sid Claim, and MAY
            # contain both. If a sid Claim is not present, the intent is that
            # all sessions at the RP for the End-User identified by the iss and
            # sub Claims be logged out.
            and (data.get("sub") or data.get("sid"))
            # As described in Section 2.4, inclusion of a nonce Claim in a
            # Logout Token is prohibited to prevent its misuse as an ID Token.
            and "nonce" not in data
        ):
            raise forms.ValidationError("The logout token contains invalid claims.")

        # Here, we deviate from the spec. We simply have no efficient way of
        # looking up sessions just by the `sid`.
        if not data.get("sub"):
            raise forms.ValidationError("The logout token must contain `sub`.")

        self.logout_data = data
        return logout_token
