from allauth.account.models import EmailAddress
from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class GitHubAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("html_url")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url")


class GitHubProvider(OAuth2Provider):
    id = "github"
    name = "GitHub"
    account_class = GitHubAccount
    oauth2_adapter_class = GitHubOAuth2Adapter

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

    def extract_extra_data(self, data):
        if "emails" in data:
            data = dict(data)
            data.pop("emails")
        return data

    def extract_email_addresses(self, data):
        ret = []
        for email in data.get("emails", []):
            ret.append(
                EmailAddress(
                    email=email["email"],
                    primary=email["primary"],
                    verified=email["verified"],
                )
            )
        return ret


provider_classes = [GitHubProvider]
