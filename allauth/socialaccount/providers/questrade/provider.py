from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.questrade.views import QuestradeOAuth2Adapter


class QuestradeAccount(ProviderAccount):
    pass


class QuestradeProvider(OAuth2Provider):
    id = "questrade"
    name = "Questrade"
    account_class = QuestradeAccount
    oauth2_adapter_class = QuestradeOAuth2Adapter

    def extract_uid(self, data):
        return str(data["userId"])


provider_classes = [QuestradeProvider]
