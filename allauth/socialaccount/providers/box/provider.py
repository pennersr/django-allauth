from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.box.views import BoxOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class BoxOAuth2Account(ProviderAccount):
    pass


class BoxOAuth2Provider(OAuth2Provider):
    id = "box"
    name = "Box"
    account_class = BoxOAuth2Account
    oauth2_adapter_class = BoxOAuth2Adapter

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        return dict(name=data.get("display_name"), email=data.get("email"))


provider_classes = [BoxOAuth2Provider]
