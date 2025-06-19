from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.lemonldap.views import LemonLDAPOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class LemonLDAPAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("picture")


class LemonLDAPProvider(OAuth2Provider):
    id = "lemonldap"
    name = "LemonLDAP::NG"
    account_class = LemonLDAPAccount
    oauth2_adapter_class = LemonLDAPOAuth2Adapter

    def get_default_scope(self):
        return ["openid", "profile", "email"]

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("preferred_username"),
            name=data.get("name"),
            picture=data.get("picture"),
        )


provider_classes = [LemonLDAPProvider]
