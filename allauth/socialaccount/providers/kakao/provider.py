from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class KakaoAccount(ProviderAccount):

    def get_avatar_url(self):
        return self.account.extra_data.get(
            'properties', {}).get('thumbnail_image')

    def to_str(self):
        return self.account.extra_data.get(
            'properties', {}).get(
            'nickname', self.account.uid)


class KakaoProvider(OAuth2Provider):
    id = 'kakao'
    name = 'Kakao'
    account_class = KakaoAccount

    def extract_uid(self, data):
        return str(data['id'])


provider_classes = [KakaoProvider]
