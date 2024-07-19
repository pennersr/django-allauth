from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.soundcloud.views import (
    SoundCloudOAuth2Adapter,
)


class SoundCloudAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("permalink_url")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url")


class SoundCloudProvider(OAuth2Provider):
    id = "soundcloud"
    name = "SoundCloud"
    account_class = SoundCloudAccount
    oauth2_adapter_class = SoundCloudOAuth2Adapter

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            name=data.get("full_name"),
            username=data.get("username"),
            email=data.get("email"),
        )


provider_classes = [SoundCloudProvider]
