from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class QQAccount(ProviderAccount):
    def get_profile_url(self):
        # profile_url = "u/3195025850"
        return 'http://www.qq.com/'

    def get_avatar_url(self):
        return self.account.extra_data.get('figureurl_qq_1')

    def to_str(self):
        dflt = super(QQAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class QQProvider(OAuth2Provider):
    id = 'qq'
    name = 'QQ'
    package = 'allauth.socialaccount.providers.qq'
    account_class = QQAccount

    def extract_uid(self, data):
        return data['idstr']

    def extract_common_fields(self, data):
        return dict(username=data.get('nickname'),
                    name=data.get('name'))


providers.registry.register(QQProvider)
