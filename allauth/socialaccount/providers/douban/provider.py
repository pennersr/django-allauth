from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.douban.views import DoubanOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DoubanAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("alt")

    def get_avatar_url(self):
        return self.account.extra_data.get("large_avatar")


class DoubanProvider(OAuth2Provider):
    id = "douban"
    name = "Douban"
    account_class = DoubanAccount
    oauth2_adapter_class = DoubanOAuth2Adapter

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        """
        Extract data from profile json to populate user instance.

        In Douban profile API:

        - id: a digital string, will never change
        - uid: defaults to id, but can be changed once, used in profile
          url, like slug
        - name: display name, can be changed every 30 days

        So we should use `id` as username here, other than `uid`.
        Also use `name` as `first_name` for displaying purpose.
        """
        return {
            "username": data["id"],
            "first_name": data.get("name", ""),
        }


provider_classes = [DoubanProvider]
