from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.gitlab.views import GitLabOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class GitLabAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("web_url")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url")


class GitLabProvider(OAuth2Provider):
    id = "gitlab"
    name = "GitLab"
    account_class = GitLabAccount
    oauth2_adapter_class = GitLabOAuth2Adapter

    def get_default_scope(self):
        return ["read_user"]

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("username"),
            name=data.get("name"),
        )


provider_classes = [GitLabProvider]
