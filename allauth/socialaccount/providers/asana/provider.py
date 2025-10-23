from allauth.socialaccount.providers.asana.views import AsanaOAuth2Adapter
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AsanaAccount(ProviderAccount):
    pass


class AsanaProvider(OAuth2Provider):
    id = "asana"
    name = "Asana"
    account_class = AsanaAccount
    oauth2_adapter_class = AsanaOAuth2Adapter

    def extract_uid(self, data):
        if "gid" not in data:
            # `id` is legacy: https://developers.asana.com/reference/getuser
            return str(data["id"])
        return str(data["gid"])

    def extract_common_fields(self, data):
        return dict(email=data.get("email"), name=data.get("name"))


provider_classes = [AsanaProvider]
