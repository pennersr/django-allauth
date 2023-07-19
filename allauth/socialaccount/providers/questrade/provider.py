from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class QuestradeAccount(ProviderAccount):
    pass


class QuestradeProvider(OAuth2Provider):
    id = "questrade"
    name = "Questrade"
    account_class = QuestradeAccount

    def extract_uid(self, data):
        return str(data["userId"])


provider_classes = [QuestradeProvider]
