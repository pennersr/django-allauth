from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.twentythreeandme.views import (
    TwentyThreeAndMeOAuth2Adapter,
)


class TwentyThreeAndMeAccount(ProviderAccount):
    pass


class TwentyThreeAndMeProvider(OAuth2Provider):
    id = "twentythreeandme"
    slug = "23andme"
    name = "23andMe"
    account_class = TwentyThreeAndMeAccount
    oauth2_adapter_class = TwentyThreeAndMeOAuth2Adapter

    def extract_uid(self, data):
        return data["id"]

    def get_default_scope(self):
        scope = ["basic"]
        return scope

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
        )


provider_classes = [TwentyThreeAndMeProvider]
