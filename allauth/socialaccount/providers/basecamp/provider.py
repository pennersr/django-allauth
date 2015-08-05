from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class BasecampAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('html_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_url')

    def to_str(self):
        dflt = super(BasecampAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class BasecampProvider(OAuth2Provider):
    id = 'basecamp'
    name = 'Basecamp'
    package = 'allauth.socialaccount.providers.basecamp'
    account_class = BasecampAccount

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email_address'),
                    username=data.get('email_address'),
                    name=data.get('name'))


providers.registry.register(BasecampProvider)
