"""
Provider for Patreon
"""
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class StravaAccount(ProviderAccount):
    pass


class StravaProvider(OAuth2Provider):
    id = "strava"
    name = "strava"
    account_class = StravaAccount

    def get_default_scope(self):
        return ["activity:read"]

    def extract_uid(self, data):
        return data.get("id")

    def extract_common_fields(self, data):
        return {"username": data.get("username"), "email": data.get("email")}


provider_classes = [StravaProvider]
