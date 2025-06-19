import requests

from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AppleAccount(ProviderAccount):
    def to_str(self):
        email = self.account.extra_data.get("email")
        if email and not email.lower().endswith("@privaterelay.appleid.com"):
            return email

        name = self.account.extra_data.get("name") or {}
        if name.get("firstName") or name.get("lastName"):
            full_name = f"{name['firstName'] or ''} {name['lastName'] or ''}"
            full_name = full_name.strip()
            if full_name:
                return full_name

        return super().to_str()


class AppleProvider(OAuth2Provider):
    id = "apple"
    name = "Apple"
    account_class = AppleAccount
    oauth2_adapter_class = AppleOAuth2Adapter
    supports_token_authentication = True

    def extract_uid(self, data):
        return str(data["sub"])

    def extract_common_fields(self, data):
        fields = {"email": data.get("email")}

        # If the name was provided
        name = data.get("name")
        if name:
            fields["first_name"] = name.get("firstName", "")
            fields["last_name"] = name.get("lastName", "")

        return fields

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        verified = data.get("email_verified")
        if isinstance(verified, str):
            verified = verified.lower() == "true"
        if email:
            ret.append(
                EmailAddress(
                    email=email,
                    verified=verified,
                    primary=True,
                )
            )
        return ret

    def get_default_scope(self):
        scopes = ["name"]
        if QUERY_EMAIL:
            scopes.append("email")
        return scopes

    def verify_token(self, request, token):
        from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter

        id_token = token.get("id_token")
        if not id_token:
            raise get_adapter().validation_error("invalid_token")
        try:
            identity_data = AppleOAuth2Adapter.get_verified_identity_data(
                self, id_token
            )
        except (OAuth2Error, requests.RequestException) as e:
            raise get_adapter().validation_error("invalid_token") from e
        login = self.sociallogin_from_response(request, identity_data)
        return login

    def get_auds(self):
        return [aud.strip() for aud in self.app.client_id.split(",")]


provider_classes = [AppleProvider]
