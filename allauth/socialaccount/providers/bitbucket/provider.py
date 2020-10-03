from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class BitbucketAccount(ProviderAccount):
    def get_profile_url(self):
        return "http://bitbucket.org/" + self.account.extra_data["username"]

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar")

    def get_username(self):
        return self.account.extra_data["username"]

    def to_str(self):
        return self.get_username()


class BitbucketProvider(OAuthProvider):
    id = "bitbucket"
    name = "Bitbucket"
    account_class = BitbucketAccount

    def extract_uid(self, data):
        return data["username"]

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            first_name=data.get("first_name"),
            username=data.get("username"),
            last_name=data.get("last_name"),
        )


provider_classes = [BitbucketProvider]
