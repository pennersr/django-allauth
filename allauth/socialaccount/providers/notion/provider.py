from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class NotionAccount(ProviderAccount):
    def get_name(self):
        return self.account.extra_data.get('owner', {}).get('user', {}).get('name', "")

    def get_workspace_name(self):
        return self.account.extra_data.get("workspace_name")

    def get_workspace_icon(self):
        return self.account.extra_data.get("workspace_icon")

    def get_avatar_url(self):
        return self.account.extra_data.get('owner', {}).get('user', {}).get("avatar_url")

    def to_str(self):
        dflt = super(NotionAccount, self).to_str()
        name = self.account.extra_data.get('owner', {}).get('user', {}).get('name', "")
        workspace_name = self.account.extra_data.get("workspace_name", "")
        return f'{name} ({workspace_name})'


class NotionProvider(OAuth2Provider):
    id = "notion"
    name = "Notion"
    account_class = NotionAccount

    def get_user(self, data):
        return data.get('owner', {}).get('user', {})

    def extract_uid(self, data):
        """
        The unique identifer for Notion is a combination of the User ID and the Workspace ID they have
        authorized the application with.
        """
        user_id = self.get_user(data).get('id')
        workspace_id = data.get('workspace_id')
        return f'user-{user_id}_workspace-{workspace_id}'

    def extract_common_fields(self, data):
        user = self.get_user(data)
        person = user.get('person', {})
        user['email'] = person.get('email')
        return user

    def extract_email_addresses(self, data):
        user = self.get_user(data)
        person = user.get('person', {})
        email = person.get('email')
        ret = []
        if email:
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [NotionProvider]