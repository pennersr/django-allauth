from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.pinterest.views import PinterestOAuth2Adapter


class PinterestAccount(ProviderAccount):
    def get_username(self):
        return self.account.extra_data.get("username")

    def get_profile_url(self):
        # v5 extra_data not same as v1
        username = self.get_username()
        if username:
            return "https://www.pinterest.com/{}/".format(username)
        return self.account.extra_data.get("url")

    def get_avatar_url(self):
        return self.account.extra_data.get("profile_image")


class PinterestProvider(OAuth2Provider):
    id = "pinterest"
    name = "Pinterest"
    account_class = PinterestAccount
    oauth2_adapter_class = PinterestOAuth2Adapter

    @property
    def api_version(self):
        return self.get_settings().get("API_VERSION", "v1")

    def get_default_scope(self):
        # See: https://developers.pinterest.com/docs/api/overview/#scopes
        if self.api_version == "v5":
            # See: https://developers.pinterest.com/docs/getting-started/scopes/
            return ["user_accounts:read"]
        elif self.api_version == "v3":
            return ["read_users"]
        return ["read_public"]

    def extract_extra_data(self, data):
        if self.api_version == "v5":
            return data
        return data.get("data", {})

    def extract_uid(self, data):
        if self.api_version == "v5":
            return data["username"]
        return str(data["data"]["id"])

    def extract_common_fields(self, data):
        if self.api_version == "v5":
            return dict(username=data["username"])
        return dict(
            first_name=data.get("data", {}).get("first_name"),
            last_name=data.get("data", {}).get("last_name"),
        )


provider_classes = [PinterestProvider]
