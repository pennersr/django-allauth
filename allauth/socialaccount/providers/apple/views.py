import jwt
import json
import requests
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.http import urlencode

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import AppleProvider
from .client import AppleOAuth2Client

from allauth.socialaccount.models import SocialLogin, SocialToken, SocialApp

from django.http import HttpResponseRedirect


class AppleOAuth2Adapter(OAuth2Adapter):
    provider_id = AppleProvider.id
    access_token_url = 'https://appleid.apple.com/auth/token'
    authorize_url = 'https://appleid.apple.com/auth/authorize'
    public_key_url = 'https://appleid.apple.com/auth/keys'
    
    def get_public_key(self):
        apple_public_key = requests.get(self.public_key_url).json()['keys'][0]
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(
            json.dumps(apple_public_key)
        )
        return public_key

    def get_client_id(self, provider):
        app = SocialApp.objects.get(provider=provider.id)
        return app.client_id

    def parse_token(self, data):
        token = SocialToken(token=data['access_token'])
        token.token_secret = data.get('refresh_token', '')

        public_key = self.get_public_key()
        provider = self.get_provider()
        client_id = self.get_client_id(provider)

        token.user_data = jwt.decode(
            data['id_token'], 
            public_key,
            algorithm="RS256",
            verify=True,
            audience=client_id
        )
        expires_in = data.get(self.expires_in_key, None)
        if expires_in:
            token.expires_at = timezone.now() + timedelta(
                seconds=int(expires_in))
        return token

    def complete_login(self, request, app, token, **kwargs):
        extra_data = token.user_data
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login

class AppleOAuth2LoginView(OAuth2LoginView):
    """ Custom AppleOAuth2LoginView to return AppleOAuth2Client """

    def get_client(self, request, app):
        client = super(AppleOAuth2LoginView, self).get_client(request, app)
        apple_client = AppleOAuth2Client(
            client.request, client.consumer_key, client.consumer_secret,
            client.access_token_method, client.access_token_url,
            client.callback_url, client.scope)
        return apple_client

class AppleOAuth2CallbackView(OAuth2CallbackView):
    """ 
    Custom OAuth2CallbackView because `Sign In With Apple`:
        * returns AppleOAuth2Client
        * Apple requests callback by POST
    """

    def get_client(self, request, app):
        client = super(AppleOAuth2CallbackView, self).get_client(request, app)
        apple_client = AppleOAuth2Client(
            client.request, client.consumer_key, client.consumer_secret,
            client.access_token_method, client.access_token_url,
            client.callback_url, client.scope)
        return apple_client

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            url = request.build_absolute_uri(request.get_full_path())
            params = {
                'code':request.POST.get('code'),
                'state':request.POST.get('state'),
            }
            return HttpResponseRedirect('%s?%s' % (url, urlencode(params)))
        if request.method == 'GET':
            return super().dispatch(request, *args, **kwargs)


oauth2_login = AppleOAuth2LoginView.adapter_view(AppleOAuth2Adapter)
oauth2_callback = csrf_exempt(AppleOAuth2CallbackView.adapter_view(AppleOAuth2Adapter))
