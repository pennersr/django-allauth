from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class AtlassianOAuth2Adapter(OAuth2Adapter):
    provider_id = "atlassian"
    access_token_url = "https://api.atlassian.com/oauth/token"
    authorize_url = "https://auth.atlassian.com/authorize"
    profile_url = "https://api.atlassian.com/me"

    def complete_login(self, request, app, access_token, **kwargs):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        response = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )
        response.raise_for_status()
        data = response.json()
        return self.get_provider().sociallogin_from_response(request, data)


oauth2_login = OAuth2LoginView.adapter_view(AtlassianOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AtlassianOAuth2Adapter)
