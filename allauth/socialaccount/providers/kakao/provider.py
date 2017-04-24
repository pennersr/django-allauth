from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class KakaoAccount(ProviderAccount):
    @property
    def properties(self):
        return self.account.extra_data['properties']

    def get_avatar_url(self):
        return self.properties['profile_image']

    def to_str(self):
        dflt = super(KakaoAccount, self).to_str()
        return self.properties['nickname'] or dflt


class KakaoProvider(OAuth2Provider):
    id = 'kakao'
    name = 'Kakao'
    account_class = KakaoAccount

    def extract_uid(self, data):
        return str(data['id'])


provider_classes = [KakaoProvider]
