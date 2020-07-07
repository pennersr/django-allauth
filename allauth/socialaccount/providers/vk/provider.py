from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class VKAccount(ProviderAccount):
    def get_profile_url(self):
        return 'https://vk.com/id%s' % self.account.extra_data.get('id')

    def get_avatar_url(self):
        ret = None
        photo_big_url = self.account.extra_data.get('photo_big')
        photo_medium_url = self.account.extra_data.get('photo_medium')
        if photo_big_url:
            return photo_big_url
        elif photo_medium_url:
            return photo_medium_url
        else:
            return ret

    def to_str(self):
        first_name = self.account.extra_data.get('first_name', '')
        last_name = self.account.extra_data.get('last_name', '')
        name = ' '.join([first_name, last_name]).strip()
        return name or super(VKAccount, self).to_str()


class VKProvider(OAuth2Provider):
    id = 'vk'
    name = 'VK'
    account_class = VKAccount

    def get_default_scope(self):
        scope = []
        if app_settings.QUERY_EMAIL:
            scope.append('email')
        return scope

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    last_name=data.get('last_name'),
                    username=data.get('screen_name'),
                    first_name=data.get('first_name'))


provider_classes = [VKProvider]
