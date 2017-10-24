import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import MeetupProvider


class MeetupOAuth2Adapter(OAuth2Adapter):
    provider_id = MeetupProvider.id
    access_token_url = 'https://secure.meetup.com/oauth2/access'
    authorize_url = 'https://secure.meetup.com/oauth2/authorize'
    profile_url = 'https://api.meetup.com/2/member/self'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token})
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(MeetupOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MeetupOAuth2Adapter)
