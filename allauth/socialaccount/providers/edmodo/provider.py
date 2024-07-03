from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.edmodo.views import EdmodoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class EdmodoAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("profile_url")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url")

    def to_str(self):
        return self.account.extra_data.get("username") or super().to_str()


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
        return dict(
            avatar_url=data.get("avatars").get("large"),
            email=data.get("email"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            profile_url=data.get("url"),
            user_type=data.get("type"),
            username=data.get("username"),
        )


provider_classes = [EdmodoProvider]
