from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.twitter_oauth2.views import (
    TwitterOAuth2Adapter,
)


class TwitterOAuth2Account(ProviderAccount):
    def get_username(self):
        return self.account.extra_data.get("username")

    def get_profile_url(self):
        username = self.get_username()
        if username:
            return "https://twitter.com/" + username
        return None

    def get_avatar_url(self):
        return self.account.extra_data.get("profile_image_url")


class TwitterOAuth2Provider(OAuth2Provider):
    id = "twitter_oauth2"
    name = "Twitter"
    account_class = TwitterOAuth2Account
    oauth2_adapter_class = TwitterOAuth2Adapter
    pkce_enabled_default = True

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        return dict(
            name=data["name"],
            username=data["username"],
        )

    def get_fields(self):
        settings = self.get_settings()
        default_fields = [
            "id",
            "name",
            "username",
            "verified",
            "profile_image_url",
            "created_at",
        ]
        return settings.get("FIELDS", default_fields)

    def get_default_scope(self):
        return ["users.read", "tweet.read"]


provider_classes = [TwitterOAuth2Provider]
