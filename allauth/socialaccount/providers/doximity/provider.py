from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.doximity.views import DoximityOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DoximityAccount(ProviderAccount):
    def get_profile_url(self):
        return None

    def get_avatar_url(self):
        return self.account.extra_data.get("profile_photo")


class DoximityProvider(OAuth2Provider):
    id = "doximity"
    name = "Doximity"
    account_class = DoximityAccount
    oauth2_adapter_class = DoximityOAuth2Adapter

    def extract_uid(self, data):
        return str(data["id"])  # the Doximity id is long

    def extract_common_fields(self, data):
        return dict(
            username=data.get("email"),
            first_name=data.get("firstname"),
            last_name=data.get("lastname"),
            email=data.get("email"),
            name=data.get("full_name"),
        )

    def get_default_scope(self):
        return ["basic", "email"]


provider_classes = [DoximityProvider]
