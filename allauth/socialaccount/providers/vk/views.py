import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from allauth.socialaccount.models import SocialLogin, SocialAccount
from allauth.socialaccount.adapter import get_adapter

from .provider import VKProvider


USER_FIELDS = ['first_name',
               'last_name',
               'nickname',
               'screen_name',
               'sex',
               'bdate',
               'city',
               'country',
               'timezone',
               'photo',
               'photo_medium',
               'photo_big',
               'has_mobile',
               'contacts',
               'education',
               'online',
               'counters',
               'relation',
               'last_seen',
               'activity',
               'universities']


class VKOAuth2Adapter(OAuth2Adapter):
    provider_id = VKProvider.id
    access_token_url = 'https://oauth.vk.com/access_token'
    authorize_url = 'http://oauth.vk.com/authorize'
    profile_url = 'https://api.vk.com/method/users.get'

    def complete_login(self, request, app, token, **kwargs):
        uid = kwargs['response']['user_id']
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token,
                                    'fields': ','.join(USER_FIELDS),
                                    'user_ids': uid})
        resp.raise_for_status()
        extra_data = resp.json()['response'][0]
        # extra_data is something of the form:
        # {u'response': [{u'last_name': u'Penners', u'university_name': u'', u'photo': u'http://vk.com/images/camera_c.gif', u'sex': 2, u'photo_medium': u'http://vk.com/images/camera_b.gif', u'relation': u'0', u'timezone': 1, u'photo_big': u'http://vk.com/images/camera_a.gif', u'uid': 219004864, u'universities': [], u'city': u'1430', u'first_name': u'Raymond', u'faculty_name': u'', u'online': 1, u'counters': {u'videos': 0, u'online_friends': 0, u'notes': 0, u'audios': 0, u'photos': 0, u'followers': 0, u'groups': 0, u'user_videos': 0, u'albums': 0, u'friends': 0}, u'home_phone': u'', u'faculty': 0, u'nickname': u'', u'screen_name': u'id219004864', u'has_mobile': 1, u'country': u'139', u'university': 0, u'graduation': 0, u'activity': u'', u'last_seen': {u'time': 1377805189}}]}
        user = get_adapter() \
            .populate_new_user(last_name=extra_data.get('family_name'),
                               username=extra_data.get('screen_name'),
                               first_name=extra_data.get('given_name'))
        account = SocialAccount(extra_data=extra_data,
                                uid=str(uid),
                                provider=self.provider_id,
                                user=user)
        return SocialLogin(account)


oauth2_login = OAuth2LoginView.adapter_view(VKOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(VKOAuth2Adapter)
