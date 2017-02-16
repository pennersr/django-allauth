import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import KakaoProvider


class KakaoOAuth2Adapter(OAuth2Adapter):
    provider_id = KakaoProvider.id
    access_token_url = 'https://kauth.kakao.com/oauth/token'
    authorize_url = 'https://kauth.kakao.com/oauth/authorize'
    profile_url = 'https://kapi.kakao.com/v1/user/me'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


class KakaoCallbackView(OAuth2CallbackView):
    def get_client(self, request, app):
        client = super(KakaoCallbackView, self).get_client(request, app)
        client.consumer_secret = None   # kakao not used client_secret
        return client


oauth2_login = OAuth2LoginView.adapter_view(KakaoOAuth2Adapter)
oauth2_callback = KakaoCallbackView.adapter_view(KakaoOAuth2Adapter)
