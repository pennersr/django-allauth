from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class InstagramOAuth2Adapter(OAuth2Adapter):
    provider_id = "instagram"
    access_token_url = "https://api.instagram.com/oauth/access_token"
    authorize_url = "https://api.instagram.com/oauth/authorize"
    profile_url = "https://graph.instagram.com/me"

    def complete_login(self, request, app, token, **kwargs):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.profile_url,
                params={"access_token": token.token, "fields": ["id", "username"]},
            )
        )
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(InstagramOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(InstagramOAuth2Adapter)
