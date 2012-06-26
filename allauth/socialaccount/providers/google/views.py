import urllib
import httplib2
from django.utils import simplejson

from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CompleteView)


from models import GoogleProvider

class Scope:
    USERINFO_PROFILE = 'https://www.googleapis.com/auth/userinfo.profile'
    USERINFO_EMAIL = 'https://www.googleapis.com/auth/userinfo.email'

class GoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = GoogleProvider.id
    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    authorize_url = 'https://accounts.google.com/o/oauth2/auth'
    user_show_url = 'https://www.googleapis.com/oauth2/v1/userinfo'

    def get_user_info(self, request, app, access_token):
        params = urllib.urlencode({ 'access_token': access_token,
                                    'alt': 'json' })
        url = self.user_show_url + '?' + params
        # TODO: Proper exception handling et al
        client = httplib2.Http()
        resp, content = client.request(url, 'GET')
        extra_data = simplejson.loads(content)
        # extra_data is something of the form:
        # 
        # {u'family_name': u'Penners', u'name': u'Raymond Penners', 
        #  u'picture': u'https://lh5.googleusercontent.com/-GOFYGBVOdBQ/AAAAAAAAAAI/AAAAAAAAAGM/WzRfPkv4xbo/photo.jpg', 
        #  u'locale': u'nl', u'gender': u'male', 
        #  u'email': u'raymond.penners@gmail.com', 
        #  u'link': u'https://plus.google.com/108204268033311374519', 
        #  u'given_name': u'Raymond', u'id': u'108204268033311374519', 
        #  u'verified_email': True}
        #
        # TODO: We could use verified_email to bypass allauth email verification
        uid = str(extra_data['id'])
        data = { 'email': extra_data.get('email', ''),
                 'last_name': extra_data['family_name'],
                 'first_name': extra_data['given_name'] }
        return uid, data, extra_data

    def get_scope(self):
        settings = self.get_provider().get_settings()
        scope = settings.get('SCOPE')
        if not scope:
            scope = [Scope.USERINFO_PROFILE]
            if QUERY_EMAIL:
                scope.append(Scope.USERINFO_EMAIL)
        return scope

oauth2_login = OAuth2LoginView.adapter_view(GoogleOAuth2Adapter)
oauth2_complete = OAuth2CompleteView.adapter_view(GoogleOAuth2Adapter)

