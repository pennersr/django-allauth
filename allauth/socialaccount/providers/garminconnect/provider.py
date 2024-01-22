from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class GarminConnectAccount(ProviderAccount):
    def get_profile_url(self):
        """
        Garmin Connect API doesn't provide a profile URL
        """
        return None

    def get_avatar_url(self):
        """
        Garmin Connect API doesn't provide an avatar URL
        """
        return None

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
        return str(data['userId'])

    def extract_common_fields(self, data):
        # Garmin Connect API doesn't return any other data than userId
        return {}

    def sociallogin_from_response(self, request, response):
        return super(GarminConnectProvider, self).sociallogin_from_response(request, response)


provider_classes = [GarminConnectProvider]
