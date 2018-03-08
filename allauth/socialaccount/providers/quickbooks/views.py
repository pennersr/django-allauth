import requests
import json

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import QuickbooksOAuth2Provider


class QuickbooksOAuth2Adapter(OAuth2Adapter):
    provider_id = QuickbooksOAuth2Provider.id
    access_token_url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
    authorize_url = 'https://appcenter.intuit.com/connect/oauth2'
    profile_test = 'https://sandbox-accounts.platform.intuit.com/v1/openid_connect/userinfo'
    profile_url = 'https://accounts.platform.intuit.com/v1/openid_connect/userinfo'
    # See:
    # http://developer.linkedin.com/forum/unauthorized-invalid-or-expired-token-immediately-after-receiving-oauth2-token?page=1 # noqa
    profile_url_method = 'GET'
    access_token_method = 'POST'

    def complete_login(self, request, app, token, **kwargs):
        resp = self.get_user_info(token)
        extra_data = resp
        return self.get_provider().sociallogin_from_response(
            request, extra_data)


    def get_user_info(self, token):
        from config.settings import QBO_TEST
        auth_header = 'Bearer ' + token.token
        headers = {'Accept': 'application/json', 'Authorization': auth_header, 'accept': 'application/json'}
        if QBO_TEST:
            r = requests.get(self.profile_test, headers=headers)
        else:
            r = requests.get(self.profile_url, headers=headers)
        status_code = r.status_code
        response = json.loads(r.text)
        return response


oauth2_login = OAuth2LoginView.adapter_view(QuickbooksOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(QuickbooksOAuth2Adapter)