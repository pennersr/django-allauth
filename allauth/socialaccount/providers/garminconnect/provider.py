from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider

class GarminConnectAccount(ProviderAccount):
    def get_profile_url(self):
        id = self.account.extra_data.get("id")
        if id:
            return f"https://connect.garmin.com/modern/profile/{id}"
        return None

    def get_avatar_url(self):
        avatar = self.account.extra_data.get("avatar")
        if avatar:
            return avatar
        return None

    def to_str(self):
        name = super(GarminConnectAccount, self).to_str()
        return self.account.extra_data.get("name", name)


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