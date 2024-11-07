from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class MeetupOAuth2Adapter(OAuth2Adapter):
    provider_id = "meetup"
    access_token_url = "https://secure.meetup.com/oauth2/access"  # nosec
    authorize_url = "https://secure.meetup.com/oauth2/authorize"
    profile_url = "https://api.meetup.com/2/member/self"

    def complete_login(self, request, app, token, **kwargs):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(self.profile_url, params={"access_token": token.token})
        )
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(MeetupOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MeetupOAuth2Adapter)
