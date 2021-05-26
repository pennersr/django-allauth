from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import (
    ProviderAccount,
    ProviderException,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class GlobusAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("web_url", "dflt")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url", "dflt")

    def to_str(self):
        dflt = super(GlobusAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class GlobusProvider(OAuth2Provider):
    id = "globus"
    name = "Globus"
    account_class = GlobusAccount

    def extract_uid(self, data):
        if "sub" not in data:
            raise ProviderException("Globus OAuth error", data)
        return str(data["sub"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("preferred_username"),
            name=data.get("name"),
        )

    def get_default_scope(self):
        scope = ["openid", "profile", "offline_access"]
        if app_settings.QUERY_EMAIL:
            scope.append("email")
        return scope


provider_classes = [GlobusProvider]
