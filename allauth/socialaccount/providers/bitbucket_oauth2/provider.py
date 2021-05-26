from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class BitbucketOAuth2Account(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("links", {}).get("html", {}).get("href")

    def get_avatar_url(self):
        return self.account.extra_data.get("links", {}).get("avatar", {}).get("href")

    def to_str(self):
        dflt = super(BitbucketOAuth2Account, self).to_str()
        return self.account.extra_data.get("display_name", dflt)


class BitbucketOAuth2Provider(OAuth2Provider):
    id = "bitbucket_oauth2"
    name = "Bitbucket"
    account_class = BitbucketOAuth2Account

    def extract_uid(self, data):
        return data["username"]

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("username"),
            name=data.get("display_name"),
        )


provider_classes = [BitbucketOAuth2Provider]
