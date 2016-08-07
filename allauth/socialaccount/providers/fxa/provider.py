from django.conf import settings

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

_FXA_SETTINGS = getattr(
    settings, 'SOCIALACCOUNT_PROVIDERS', {}).get('fxa', {})
FXA_OAUTH_ENDPOINT = _FXA_SETTINGS.get(
    'OAUTH_ENDPOINT',
    'https://oauth.accounts.firefox.com/v1')
FXA_PROFILE_ENDPOINT = _FXA_SETTINGS.get(
    'PROFILE_ENDPOINT',
    'https://profile.accounts.firefox.com/v1')


class FirefoxAccountsAccount(ProviderAccount):

    def to_str(self):
        return self.account.uid


class FirefoxAccountsProvider(OAuth2Provider):
    id = 'fxa'
    name = 'Firefox Accounts'
    account_class = FirefoxAccountsAccount

    def get_default_scope(self):
        return ['profile']

    def extract_uid(self, data):
        return str(data['uid'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'))


providers.registry.register(FirefoxAccountsProvider)
