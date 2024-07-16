from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.edx.views import EdxOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class EdxAccount(ProviderAccount):
    def get_profile_url(self):
        if self.account.extra_data["profile_image"]["has_image"]:
            return self.account.extra_data["image_url_full"]


class EdxProvider(OAuth2Provider):
    id = "edx"
    name = "Edx"
    account_class = EdxAccount
    oauth2_adapter_class = EdxOAuth2Adapter

    def get_default_scope(self):
        return ["profile"]

    def extract_uid(self, data):
        """Extract uid ('id') and ensure it's a str."""
        return str(data["username"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("username"),
            name=data.get("name"),
            user_id=data.get("user_id"),
        )


provider_classes = [EdxProvider]
