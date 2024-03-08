from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.hubic.views import HubicOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class HubicAccount(ProviderAccount):
    pass


class HubicProvider(OAuth2Provider):
    id = "hubic"
    name = "Hubic"
    account_class = HubicAccount
    oauth2_adapter_class = HubicOAuth2Adapter

    def extract_uid(self, data):
        return str(data["email"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("firstname").lower() + data.get("lastname").lower(),
            first_name=data.get("firstname"),
            last_name=data.get("lastname"),
        )


provider_classes = [HubicProvider]
