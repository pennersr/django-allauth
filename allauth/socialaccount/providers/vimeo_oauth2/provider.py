"""
Provider for Patreon
"""
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class VimeoOAuth2Account(ProviderAccount):
    pass


class VimeoOAuth2Provider(OAuth2Provider):
    id = "vimeo_oauth2"
    name = "Vimeo"
    account_class = VimeoOAuth2Account

    def get_default_scope(self):
        return ["public", "private"]

    def extract_uid(self, data):
        return data.get("uri").split("/")[-1]

    def extract_common_fields(self, data):
        return {
            "fullname": data.get("name"),
        }


provider_classes = [VimeoOAuth2Provider]
