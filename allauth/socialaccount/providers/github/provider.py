from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class GitHubAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("html_url")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url")

    def to_str(self):
        dflt = super(GitHubAccount, self).to_str()
        return next(
            value
            for value in (
                self.account.extra_data.get("name", None),
                self.account.extra_data.get("login", None),
                dflt,
            )
            if value is not None
        )


class GitHubProvider(OAuth2Provider):
    id = "github"
    name = "GitHub"
    account_class = GitHubAccount

    def get_default_scope(self):
        scope = []
        if app_settings.QUERY_EMAIL:
            scope.append("user:email")
        return scope

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("login"),
            name=data.get("name"),
        )


provider_classes = [GitHubProvider]
