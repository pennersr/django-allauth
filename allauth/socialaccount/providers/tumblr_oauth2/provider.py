from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.tumblr_oauth2.views import TumblrOAuth2Adapter


class TumblrAccount(ProviderAccount):
    def get_profile_url(self):
        return "https://%s.tumblr.com/" % self.account.extra_data.get("name")


class TumblrOAuth2Provider(OAuth2Provider):
    id = "tumblr_oauth2"
    name = "Tumblr"
    account_class = TumblrAccount
    oauth2_adapter_class = TumblrOAuth2Adapter

    def extract_uid(self, data):
        return data["name"]

    def extract_common_fields(self, data):
        return dict(
            first_name=data.get("name"),
        )

    def get_default_scope(self):
        return ["read"]


provider_classes = [TumblrOAuth2Provider]
