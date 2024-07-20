from allauth.socialaccount.providers.auth0.views import Auth0OAuth2Adapter
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class Auth0Account(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("picture")


class Auth0Provider(OAuth2Provider):
    id = "auth0"
    name = "Auth0"
    account_class = Auth0Account
    oauth2_adapter_class = Auth0OAuth2Adapter

    def get_default_scope(self):
        return ["openid", "profile", "email"]

    def extract_uid(self, data):
        return str(data["sub"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("username"),
            name=data.get("name"),
        )


provider_classes = [Auth0Provider]
