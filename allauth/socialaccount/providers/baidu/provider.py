from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class BaiduAccount(ProviderAccount):
    def get_profile_url(self):
        return (
            'https://openapi.baidu.com'
            '/rest/2.0/passport/users/getLoggedInUser')

    def get_avatar_url(self):
        return (
            'http://tb.himg.baidu.com/sys/portraitn/item/' +
            self.account.extra_data.get('portrait'))

    def to_str(self):
        dflt = super(BaiduAccount, self).to_str()
        return self.account.extra_data.get('uname', dflt)


class BaiduProvider(OAuth2Provider):
    id = 'baidu'
    name = 'Baidu'
    account_class = BaiduAccount

    def extract_uid(self, data):
        return data['uid']

    def extract_common_fields(self, data):
        return dict(username=data.get('uid'),
                    name=data.get('uname'))


provider_classes = [BaiduProvider]
