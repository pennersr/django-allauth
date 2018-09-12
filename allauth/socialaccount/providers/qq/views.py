import requests, re, json

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import QQProvider


class QQOAuth2Adapter(OAuth2Adapter):
    provider_id = QQProvider.id
    authorize_url = 'https://graph.qq.com/oauth2.0/authorize'
    access_token_url = 'https://graph.qq.com/oauth2.0/token'
    open_id_url = 'https://graph.qq.com/oauth2.0/me'
    profile_url = 'https://graph.qq.com/user/get_user_info'

    def complete_login(self, request, app, token, **kwargs):
        open_id_resp = requests.get(self.open_id_url, params={'access_token': token.token})
        try:
            open_id_dict = json.loads(re.match(r'callback\( ({.*}) \);', open_id_resp.text).group(1))
        except Exception:
            open_id_dict = {"client_id": "client_id", "openid": "openid"}
        openid = open_id_dict.get('openid')
        oauth_consumer_key = open_id_dict.get('client_id')
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token,
                                    'oauth_consumer_key': oauth_consumer_key,
                                    'openid': openid})
        extra_data = resp.json()
        # use the openid as uid
        extra_data['openid'] = openid
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(QQOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(QQOAuth2Adapter)
