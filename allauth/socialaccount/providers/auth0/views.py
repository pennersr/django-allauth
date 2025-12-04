from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class Auth0OAuth2Adapter(OAuth2Adapter):
    provider_id = "auth0"

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get("AUTH0_URL")

    access_token_url = f"{provider_base_url}/oauth/token"
    authorize_url = f"{provider_base_url}/authorize"
    profile_url = f"{provider_base_url}/userinfo"

    def complete_login(self, request, app, token, response):
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, params={"access_token": token.token})
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(Auth0OAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(Auth0OAuth2Adapter)
