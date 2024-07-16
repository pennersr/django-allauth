from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.bitbucket_oauth2.views import (
    BitbucketOAuth2Adapter,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class BitbucketOAuth2Account(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("links", {}).get("html", {}).get("href")

    def get_avatar_url(self):
        return self.account.extra_data.get("links", {}).get("avatar", {}).get("href")


class BitbucketOAuth2Provider(OAuth2Provider):
    id = "bitbucket_oauth2"
    name = "Bitbucket"
    account_class = BitbucketOAuth2Account
    oauth2_adapter_class = BitbucketOAuth2Adapter

    def extract_uid(self, data):
        return data["username"]

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("username"),
            name=data.get("display_name"),
        )


provider_classes = [BitbucketOAuth2Provider]
