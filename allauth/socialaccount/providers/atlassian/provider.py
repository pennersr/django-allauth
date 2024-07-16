from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

from .views import AtlassianOAuth2Adapter


class AtlassianAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("picture")


class AtlassianProvider(OAuth2Provider):
    id = "atlassian"
    name = "Atlassian"
    account_class = AtlassianAccount
    oauth2_adapter_class = AtlassianOAuth2Adapter

    def extract_uid(self, data):
        return data["account_id"]

    def extract_common_fields(self, data):
        return {
            "email": data.get("email"),
            "name": data.get("name"),
            "username": data.get("nickname"),
            "email_verified": data.get("email_verified"),
        }

    def get_default_scope(self):
        return ["read:me"]

    def get_auth_params(self):
        params = super().get_auth_params()
        params.update({"audience": "api.atlassian.com", "prompt": "consent"})
        return params


provider_classes = [AtlassianProvider]
