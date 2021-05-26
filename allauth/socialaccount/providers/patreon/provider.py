"""
Provider for Patreon
"""

from django.conf import settings

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


API_VERSION = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("patreon", {})
    .get("VERSION", "v1")
)
USE_API_V2 = True if API_VERSION == "v2" else False
API_URL = "https://www.patreon.com/api/oauth2/" + (API_VERSION if USE_API_V2 else "api")


class PatreonAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("attributes").get("thumb_url")


class PatreonProvider(OAuth2Provider):
    id = "patreon"
    name = "Patreon"
    account_class = PatreonAccount

    def get_default_scope(self):
        if USE_API_V2:
            return [
                "identity",
                "identity[email]",
                "campaigns",
                "campaigns.members",
            ]
        return ["pledges-to-me", "users", "my-campaign"]

    def extract_uid(self, data):
        return data.get("id")

    def extract_common_fields(self, data):
        details = data["attributes"]
        return {
            "email": details.get("email"),
            "fullname": details.get("full_name"),
            "first_name": details.get("first_name"),
            "last_name": details.get("last_name"),
        }


provider_classes = [PatreonProvider]
