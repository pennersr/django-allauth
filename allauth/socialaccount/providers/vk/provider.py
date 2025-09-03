from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.vk.views import VKOAuth2Adapter


class VKAccount(ProviderAccount):
    def get_profile_url(self):
        return "https://vk.ru/id%s" % self.account.extra_data.get("id")

    def get_avatar_url(self):
        ret = None
        photo_big_url = self.account.extra_data.get("photo_big")
        photo_medium_url = self.account.extra_data.get("photo_medium")
        if photo_big_url:
            return photo_big_url
        elif photo_medium_url:
            return photo_medium_url
        else:
            return ret


class VKProvider(OAuth2Provider):
    id = "vk"
    name = "VK"
    account_class = VKAccount
    oauth2_adapter_class = VKOAuth2Adapter
    pkce_enabled_default = True

    def get_default_scope(self):
        scope = []
        if app_settings.QUERY_EMAIL:
            scope.append("email")
        return scope

    def extract_uid(self, data):
        return str(data["user_id"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            last_name=data.get("last_name"),
            username=data.get("screen_name"),
            first_name=data.get("first_name"),
            phone=data.get("phone"),
        )


provider_classes = [VKProvider]
