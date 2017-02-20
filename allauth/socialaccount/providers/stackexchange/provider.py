from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class StackExchangeAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('html_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_url')

    def to_str(self):
        dflt = super(StackExchangeAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class StackExchangeProvider(OAuth2Provider):
    id = 'stackexchange'
    name = 'Stack Exchange'
    account_class = StackExchangeAccount

    def get_site(self):
        settings = self.get_settings()
        return settings.get('SITE', 'stackoverflow')

    def extract_uid(self, data):
        # `user_id` varies if you use the same account for
        # e.g. StackOverflow and ServerFault. Therefore, we pick
        # `account_id`.
        uid = str(data['account_id'])
        return uid

    def extract_common_fields(self, data):
        return dict(username=data.get('display_name'))


providers.registry.register(StackExchangeProvider)
