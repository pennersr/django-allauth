from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.edmodo.views import EdmodoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class EdmodoAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("profile_url")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url")


class EdmodoProvider(OAuth2Provider):
    id = "edmodo"
    name = "Edmodo"
    account_class = EdmodoAccount
    oauth2_adapter_class = EdmodoOAuth2Adapter

    def get_default_scope(self):
        return ["basic"]

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email", ""),
        )

    def extract_extra_data(self, data):
        ret = dict(data)
        # NOTE: For backwards compatibility
        ret["user_type"] = data.get("type")
        ret["profile_url"] = data.get("url")
        ret["avatar_url"] = data.get("avatars", {}).get("large")
        # (end NOTE)
        return ret


provider_classes = [EdmodoProvider]
