import json
import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import QuickBooksOAuth2Provider


class QuickBooksOAuth2Adapter(OAuth2Adapter):
    provider_id = QuickBooksOAuth2Provider.id
    access_token_url = \
        'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
    authorize_url = \
        'https://appcenter.intuit.com/connect/oauth2'
    profile_test = 'https://sandbox-accounts.platform.intuit.com/v1/openid_connect/userinfo' # NOQA
    profile_url = \
        'https://accounts.platform.intuit.com/v1/openid_connect/userinfo'
    profile_url_method = 'GET'
    access_token_method = 'POST'

    def complete_login(self, request, app, token, **kwargs):
        resp = self.get_user_info(token)
        extra_data = resp
        return self.get_provider().sociallogin_from_response(
            request, extra_data)

    def get_user_info(self, token):
        auth_header = 'Bearer ' + token.token
        headers = {'Accept': 'application/json',
                   'Authorization': auth_header,
                   'accept': 'application/json'
                   }
        QBO_sandbox = self.get_provider().get_settings().get('SANDBOX', False)
        if QBO_sandbox:
            r = requests.get(self.profile_test, headers=headers)
        else:
            r = requests.get(self.profile_url, headers=headers)
#        status_code = r.status_code
        response = json.loads(r.text)
        return response


oauth2_login = OAuth2LoginView.adapter_view(QuickBooksOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(QuickBooksOAuth2Adapter)
