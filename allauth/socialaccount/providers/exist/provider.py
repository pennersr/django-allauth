from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class ExistAccount(ProviderAccount):
    def get_profile_url(self):
        username = self.account.extra_data.get("username")
        return 'https://exist.io/api/1/users/{}/profile/'.format(username)

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar')

    def to_str(self):
        name = super(ExistAccount, self).to_str()
        return self.account.extra_data.get('name', name)


class ExistProvider(OAuth2Provider):
    id = 'exist'
    name = 'Exist.io'
    account_class = ExistAccount

    def extract_uid(self, data):
        return data.get('id')

    def extract_common_fields(self, data):
        extra_common = super(ExistProvider, self).extract_common_fields(data)
        extra_common.update(
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
        )
        return extra_common

    def get_default_scope(self):
        return ['read']


provider_classes = [ExistProvider]
