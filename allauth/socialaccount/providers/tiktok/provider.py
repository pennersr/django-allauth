from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.tiktok.views import TiktokOAuth2Adapter


class TiktokAccount(ProviderAccount):

    def get_username(self):
        return self.account.extra_data.get("username")

    def get_display_name(self):
        return self.account.extra_data.get("display_name")

    def get_profile_url(self):
        return self.account.extra_data.get("profile_deep_link")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url")

    def to_str(self):
        username = self.get_username()
        return username or super(TiktokAccount, self).to_str()


class TiktokProvider(OAuth2Provider):
    id = "tiktok"
    name = "Tiktok"
    account_class = TiktokAccount
    oauth2_adapter_class = TiktokOAuth2Adapter
    pkce_enabled_default = False

    def extract_uid(self, data):
        return str(data["open_id"])

    def extract_common_fields(self, data):
        return {
            "username": data.get("username"),
            "name": data.get("display_name"),
            "email": data.get("email"),
        }

    def get_default_scope(self):
        # Requires LogitKit and Scopes with user.info.basic and user.info.profile enabled
        return ["user.info.basic"]
        # return ["user.info.basic", "user.info.profile"]


provider_classes = [TiktokProvider]
