from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider
from allauth.socialaccount.providers.vimeo.views import VimeoOAuthAdapter


class VimeoAccount(ProviderAccount):
    pass


class VimeoProvider(OAuthProvider):
    id = "vimeo"
    name = "Vimeo"
    account_class = VimeoAccount
    oauth_adapter_class = VimeoOAuthAdapter

    def get_default_scope(self):
        scope = []
        return scope

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        return dict(name=data.get("display_name"), username=data.get("username"))


provider_classes = [VimeoProvider]
