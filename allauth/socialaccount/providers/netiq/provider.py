from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.netiq.views import NetIQOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class NetIQAccount(ProviderAccount):
    pass


class NetIQProvider(OAuth2Provider):
    id = "netiq"
    name = "NetIQ"
    account_class = NetIQAccount
    oauth2_adapter_class = NetIQOAuth2Adapter

    def get_default_scope(self):
        return ["openid", "profile", "email"]

    def extract_uid(self, data):
        uid_field = self.app.settings.get("uid_field", "sub")
        return str(data[uid_field])

    def extract_extra_data(self, data):
        return data

    def extract_common_fields(self, data):
        return dict(
            email=data["email"],
            last_name=data["family_name"],
            first_name=data["given_name"],
        )


provider_classes = [NetIQProvider]
