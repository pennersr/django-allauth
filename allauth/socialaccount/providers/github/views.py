import urllib
import httplib2
from django.utils import simplejson

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CompleteView)


from models import GitHubProvider

class GitHubOAuth2Adapter(OAuth2Adapter):
    provider_id = GitHubProvider.id
    access_token_url = 'https://github.com/login/oauth/access_token'
    authorize_url = 'https://github.com/login/oauth/authorize'
    user_show_url = 'https://github.com/api/v2/json/user/show'

    def get_user_info(self, request, app, access_token):
        params = urllib.urlencode({ 'access_token': access_token })
        url = self.user_show_url + '?' + params
        # TODO: Proper exception handling et al
        client = httplib2.Http()
        resp, content = client.request(url, 'GET')
        extra_data = simplejson.loads(content)['user']
        uid = str(extra_data['id'])
        data = { 'username': extra_data['login'],
                 'email': extra_data['email'],
                 'first_name': extra_data['name'] }
        return uid, data, extra_data

oauth2_login = OAuth2LoginView.adapter_view(GitHubOAuth2Adapter)
oauth2_complete = OAuth2CompleteView.adapter_view(GitHubOAuth2Adapter)

