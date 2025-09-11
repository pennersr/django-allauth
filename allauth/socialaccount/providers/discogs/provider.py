from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.discogs.views import DiscogsOAuthAdapter
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class DiscogsAccount(ProviderAccount):
    def get_username(self):
        return self.account.extra_data.get("username")

    def get_profile_url(self):
        return self.account.extra_data.get("resource_url")


class DiscogsProvider(OAuthProvider):
    id = "discogs"
    name = "discogs"
    account_class = DiscogsAccount
    oauth_adapter_class = DiscogsOAuthAdapter

    def extract_uid(self, data):
        return str(data["id"])


provider_classes = [DiscogsProvider]
