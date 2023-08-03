from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class NotionAccount(ProviderAccount):
    def get_user(self):
        return self.account.extra_data["owner"]["user"]

    def get_name(self):
        return self.get_user()["name"]

    def get_avatar_url(self):
        return self.get_user()["avatar_url"]

    def get_workspace_name(self):
        return self.account.extra_data["workspace_name"]

    def get_workspace_icon(self):
        return self.account.extra_data["workspace_icon"]

    def to_str(self):
        name = self.get_name()
        workspace = self.get_workspace_name()
        return f"{name} ({workspace})"


class NotionProvider(OAuth2Provider):
    id = "notion"
    name = "Notion"
    account_class = NotionAccount

    def extract_uid(self, data):
        """
        The unique identifer for Notion is a combination of the User ID
        and the Workspace ID they have authorized the application with.
        """
        user_id = data["owner"]["user"]["id"]
        workspace_id = data["workspace_id"]
        return "user-%s_workspace-%s" % (user_id, workspace_id)

    def extract_common_fields(self, data):
        user = data["owner"]["user"]
        user["email"] = user["person"]["email"]
        return user

    def extract_email_addresses(self, data):
        user = data["owner"]["user"]
        email = user["person"]["email"]
        return [EmailAddress(email=email, verified=True, primary=True)]


provider_classes = [NotionProvider]
