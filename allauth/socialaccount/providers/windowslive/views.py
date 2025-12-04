from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class WindowsLiveOAuth2Adapter(OAuth2Adapter):
    provider_id = "windowslive"
    access_token_url = "https://login.live.com/oauth20_token.srf"  # nosec
    authorize_url = "https://login.live.com/oauth20_authorize.srf"
    profile_url = "https://apis.live.net/v5.0/me"

    def complete_login(self, request, app, token, **kwargs):
        # example of what's returned (in python format):
        # {'first_name': 'James', 'last_name': 'Smith',
        #  'name': 'James Smith', 'locale': 'en_US', 'gender': None,
        #  'emails': {'personal': None, 'account': 'jsmith@example.com',
        #  'business': None, 'preferred': 'jsmith@example.com'},
        #  'link': 'https://profile.live.com/',
        #  'updated_time': '2014-02-07T00:35:27+0000',
        #  'id': '83605e110af6ff98'}

        with get_adapter().get_requests_session() as sess:
            headers = {"Authorization": f"Bearer {token.token}"}
            resp = sess.get(self.profile_url, headers=headers)
            resp.raise_for_status()
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(WindowsLiveOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(WindowsLiveOAuth2Adapter)
