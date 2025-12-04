from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class AgaveAdapter(OAuth2Adapter):
    provider_id = "agave"

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get("API_URL", "https://public.agaveapi.co")

    access_token_url = f"{provider_base_url}/token"
    authorize_url = f"{provider_base_url}/authorize"
    profile_url = f"{provider_base_url}/profiles/v2/me"

    def complete_login(self, request, app, token, response):
        with get_adapter().get_requests_session() as sess:
            extra_data = sess.get(
                self.profile_url,
                params={"access_token": token.token},
                headers={"Authorization": f"Bearer {token.token}"},
            )
            user_profile = extra_data.json().get("result", {})

        return self.get_provider().sociallogin_from_response(request, user_profile)


oauth2_login = OAuth2LoginView.adapter_view(AgaveAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AgaveAdapter)
