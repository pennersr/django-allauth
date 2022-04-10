from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class UNiDAYSAccount(ProviderAccount):
    pass


class UNiDAYSProvider(OAuth2Provider):
    id = "unidays"
    name = "UNiDAYS"
    account_class = UNiDAYSAccount

    def get_default_scope(self):
        scope = ["openid", "name", "email", "verification", "offline_access"]
        return scope

    def extract_uid(self, data):
        return str(data["sub"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            last_name=data.get("family_name"),
            first_name=data.get("given_name"),
        )


provider_classes = [UNiDAYSProvider]
