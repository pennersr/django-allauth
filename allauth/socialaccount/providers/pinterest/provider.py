from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class PinterestAccount(ProviderAccount):

    def get_profile_url(self):
        return self.account.extra_data.get('url')

    def to_str(self):
        dflt = super(PinterestAccount, self).to_str()
        return self.account.extra_data.get('username', dflt)


class PinterestProvider(OAuth2Provider):
    id = 'pinterest'
    name = 'Pinterest'
    account_class = PinterestAccount

    def get_default_scope(self):
        # See: https://developers.pinterest.com/docs/api/overview/#scopes
        return ['read_public']

    def extract_extra_data(self, data):
        return data.get('data', {})

    def extract_uid(self, data):
        return str(data['data']['id'])

    def extract_common_fields(self, data):
        return dict(first_name=data.get('data', {}).get('first_name'),
                    last_name=data.get('data', {}).get('last_name'))


providers.registry.register(PinterestProvider)
