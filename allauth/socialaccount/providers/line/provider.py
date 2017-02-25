from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class LineAccount(ProviderAccount):

    def get_avatar_url(self):
        return self.account.extra_data.get('pictureUrl')

    def to_str(self):
        return self.account.extra_data.get('displayName', self.account.uid)


class LineProvider(OAuth2Provider):
    id = 'line'
    name = 'Line'
    account_class = LineAccount

    def get_default_scope(self):
        return []

    def extract_uid(self, data):
        return str(data['mid'])


provider_classes = [LineProvider]
