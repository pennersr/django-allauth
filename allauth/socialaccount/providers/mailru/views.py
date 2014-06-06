import requests
from django.utils.six import iteritems
from collections import OrderedDict
from hashlib import md5
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from .provider import MRUProvider


def srtdct(d):
    return OrderedDict((sorted(iteritems(d))))


class MRUOAuth2Adapter(OAuth2Adapter):
    provider_id = MRUProvider.id
    access_token_url = 'https://connect.mail.ru/oauth/token'
    authorize_url = 'https://connect.mail.ru/oauth/authorize'
    profile_url = 'http://www.appsmail.ru/platform/api'

    def complete_login(self, request, app, token, **kwargs):
        uid = kwargs['response']['x_mailru_vid']
        params = {'method': 'users.getInfo',
                  'app_id': app.client_id,
                  'secure': '1',
                  'uids': uid}

        params = srtdct(params)
        sign = md5((''.join("%s=%s" % (key, val) for (key, val) in iteritems(params))
                    + app.secret).encode('utf-8')).hexdigest()
        params.update({'sig': sign})
        params = srtdct(params)
        response = requests.get(self.profile_url, params=params)
        extra_data = response.json()[0]
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(MRUOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MRUOAuth2Adapter)

