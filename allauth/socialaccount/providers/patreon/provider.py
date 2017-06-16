"""
Provider for Patreon
"""
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class PatreonAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get('attributes').get('thumb_url')


class PatreonProvider(OAuth2Provider):
    id = 'patreon'
    name = 'Patreon'
    account_class = PatreonAccount

    def get_default_scope(self):
        return ['pledges-to-me', 'users', 'my-campaign']

    def extract_uid(self, data):
        return data.get('id')

    def extract_common_fields(self, data):
        details = data['attributes']
        return {
            'email': details.get('email'),
            'fullname': details.get('full_name'),
            'first_name': details.get('first_name'),
            'last_name': details.get('last_name'),
        }


provider_classes = [PatreonProvider]
