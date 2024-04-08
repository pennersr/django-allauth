from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.gitea.views import GiteaOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class GiteaAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("html_url")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url")

    def to_str(self):
        dflt = super(GiteaAccount, self).to_str()
        return next(
            value
            for value in (
                self.account.extra_data.get("username", None),
                self.account.extra_data.get("login", None),
                dflt,
            )
            if value is not None
        )


class GiteaProvider(OAuth2Provider):
    id = "gitea"
    name = "Gitea"
    account_class = GiteaAccount
    oauth2_adapter_class = GiteaOAuth2Adapter

    def get_default_scope(self):
        scope = []
        return scope

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("login"),
            name=data.get("name"),
        )


provider_classes = [GiteaProvider]
