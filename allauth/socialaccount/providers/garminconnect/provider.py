from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class GarminConnectAccount(ProviderAccount):

    def to_str(self):
        """
        Garmin Connect API only provides a userId
        """
        return self.account.extra_data.get("userId")


class GarminConnectProvider(OAuthProvider):
    id = 'garmin_connect'
    name = 'Garmin Connect'
    account_class = GarminConnectAccount

    def get_default_scope(self):
        return ['read', 'write']

    def extract_uid(self, data):
        return data['userId']

    def extract_common_fields(self, data):
        # Garmin Connect API doesn't return any other data than userId
        return {}

    def sociallogin_from_response(self, request, response):
        return super().sociallogin_from_response(request, response)


provider_classes = [GarminConnectProvider]
