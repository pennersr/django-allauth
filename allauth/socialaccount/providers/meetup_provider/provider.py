from allauth.socialaccount.providers.base_provider import ProviderAccount
from allauth.socialaccount.providers.meetup_provider.views import MeetupOAuth2Adapter
from allauth.socialaccount.providers.oauth2_provider.provider import OAuth2Provider


class MeetupAccount(ProviderAccount):
    pass


class MeetupProvider(OAuth2Provider):
    id = "meetup"
    name = "Meetup"
    account_class = MeetupAccount
    oauth2_adapter_class = MeetupOAuth2Adapter

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(email=data.get("email"), name=data.get("name"))


provider_classes = [MeetupProvider]
