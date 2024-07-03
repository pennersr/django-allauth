from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.meetup.views import MeetupOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class MeetupAccount(ProviderAccount):
    def to_str(self):
        email = self.account.extra_data.get("email")
        name = self.account.extra_data.get("name") or self.account.extra_data.get(
            "photo", {}
        ).get("name")
        return email or name or super().to_str()


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
