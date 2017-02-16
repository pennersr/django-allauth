import requests

from allauth.account import app_settings
from allauth.compat import reverse
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.utils import build_absolute_uri

from .client import WeixinOAuth2Client
from .provider import WeixinProvider


class WeixinOAuth2Adapter(OAuth2Adapter):
    provider_id = WeixinProvider.id
    access_token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    profile_url = 'https://api.weixin.qq.com/sns/userinfo'

    @property
    def authorize_url(self):
        settings = self.get_provider().get_settings()
        url = settings.get(
            'AUTHORIZE_URL', 'https://open.weixin.qq.com/connect/qrconnect')
        return url

    def complete_login(self, request, app, token, **kwargs):
        openid = kwargs.get('response', {}).get('openid')
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token,
                                    'openid': openid})
        extra_data = resp.json()
        nickname = extra_data.get('nickname')
        if nickname:
            extra_data['nickname'] = nickname.encode(
                'raw_unicode_escape').decode('utf-8')
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


class WeixinOAuth2ClientMixin(object):

    def get_client(self, request, app):
        callback_url = reverse(self.adapter.provider_id + "_callback")
        protocol = (
            self.adapter.redirect_uri_protocol or
            app_settings.DEFAULT_HTTP_PROTOCOL)
        callback_url = build_absolute_uri(
            request, callback_url,
            protocol=protocol)
        provider = self.adapter.get_provider()
        scope = provider.get_scope(request)
        client = WeixinOAuth2Client(
            self.request, app.client_id, app.secret,
            self.adapter.access_token_method,
            self.adapter.access_token_url,
            callback_url,
            scope)
        return client


class WeixinOAuth2LoginView(WeixinOAuth2ClientMixin, OAuth2LoginView):
    pass


class WeixinOAuth2CallbackView(WeixinOAuth2ClientMixin, OAuth2CallbackView):
    pass


oauth2_login = WeixinOAuth2LoginView.adapter_view(WeixinOAuth2Adapter)
oauth2_callback = WeixinOAuth2CallbackView.adapter_view(WeixinOAuth2Adapter)
