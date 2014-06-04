import requests

from allauth.socialaccount.providers.openid_connect.views import (OpenidConnectAdapter,
                                                          OpenidConnectLoginView,
                                                          OpenidConnectCallbackView)

from .provider import QQProvider


class QQOAuth2Adapter(OpenidConnectAdapter):
    provider_id = QQProvider.id
    access_token_url = 'https://graph.qq.com/oauth2.0/token'
    authorize_url = 'https://graph.qq.com/oauth2.0/authorize'
    open_id_url = 'https://graph.qq.com/oauth2.0/me'
    profile_url = 'https://graph.qq.com/user/get_user_info'


    def complete_login(self, request, app, token, **kwargs):
        #uid = kwargs.get('response', {}).get('uid')
        openid = kwargs['openid']
        consumer_key = kwargs['consumer_key']
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token,
                                    'oauth_consumer_key': consumer_key,
                                    'openid': openid})
        extra_data = resp.json()
        extra_data['idstr'] = openid    # use openid as uid -> do not need to look at user profile response
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OpenidConnectLoginView.adapter_view(QQOAuth2Adapter)
oauth2_callback = OpenidConnectCallbackView.adapter_view(QQOAuth2Adapter)
