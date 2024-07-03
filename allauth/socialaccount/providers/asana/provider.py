from allauth.socialaccount.providers.asana.views import AsanaOAuth2Adapter
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AsanaAccount(ProviderAccount):
    def to_str(self):
        dflt = super().to_str()
        email = self.account.extra_data.get("email")
        name = self.account.extra_data.get("name")
        return email or name or dflt


class AsanaProvider(OAuth2Provider):
    id = "asana"
    name = "Asana"
    account_class = AsanaAccount
    oauth2_adapter_class = AsanaOAuth2Adapter

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(email=data.get("email"), name=data.get("name"))


provider_classes = [AsanaProvider]
