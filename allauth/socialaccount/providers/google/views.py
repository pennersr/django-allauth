import requests

from allauth.socialaccount import providers
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.models import (SocialLogin,
                                          SocialToken)
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .forms import GoogleConnectForm
from .provider import GoogleProvider

GOOGLE_PROFILE_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'

class GoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = GoogleProvider.id
    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    authorize_url = 'https://accounts.google.com/o/oauth2/auth'
    profile_url = GOOGLE_PROFILE_URL

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token,
                                    'alt': 'json'})
        extra_data = resp.json()
        login = self.get_provider() \
            .sociallogin_from_response(request,
                                       extra_data)
        return login

def google_complete_login(request, app, token):
    params = { 'access_token': token.token }
    resp = requests.get(GOOGLE_PROFILE_URL, params = params)
    extra_data = resp.json()
    registry = providers.registry.by_id(GoogleProvider.id)

    return registry.sociallogin_from_response(request, extra_data)

def login_by_token(request):
    ret = None
    if (request.method == 'POST'):
        form = GoogleConnectForm(request.POST)
        if form.is_valid():
            app = providers.registry.by_id(GoogleProvider.id).get_app(request)
            access_token = form.cleaned_data['access_token']
            token = SocialToken(app = app, token = access_token)
            login = google_complete_login(request, app, token)
            login.state = SocialLogin.state_from_request(request)
            ret = complete_social_login(request, login)

    return ret if ret else render_authentication_error(request)

oauth2_login = OAuth2LoginView.adapter_view(GoogleOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)
