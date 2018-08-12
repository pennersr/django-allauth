from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class QQAccount(ProviderAccount):
    def get_profile_url(self):
        return 'https://graph.qq.com/user/get_user_info'

    def get_avatar_url(self):
        return self.account.extra_data.get('figureurl_qq_2')

    def to_str(self):
        default = super(QQAccount, self).to_str()
        return self.account.extra_data.get('openid', default)


class QQProvider(OAuth2Provider):
    id = 'qq'
    name = 'QQ'
    account_class = QQAccount

    def extract_uid(self, data):
        return data['openid']

    def extract_common_fields(self, data):
        return dict(username=data.get('nickname'),
                    name=data.get('name'))


provider_classes = [QQProvider]
