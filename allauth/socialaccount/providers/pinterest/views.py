from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class PinterestOAuth2Adapter(OAuth2Adapter):
    provider_id = "pinterest"

    provider_default_url = "api.pinterest.com"
    provider_default_api_version = "v1"

    settings = app_settings.PROVIDERS.get(provider_id, {})

    provider_base_url = settings.get("PINTEREST_URL", provider_default_url)
    provider_api_version = settings.get("API_VERSION", provider_default_api_version)

    authorize_url = "https://www.pinterest.com/oauth/"
    access_token_url = f"https://{provider_base_url}/{provider_api_version}/oauth/token"
    basic_auth = True
    if provider_api_version == "v5":
        profile_url = f"https://{provider_base_url}/{provider_api_version}/user_account"
    elif provider_api_version == "v3":
        profile_url = f"https://{provider_base_url}/{provider_api_version}/users/me"
    else:
        profile_url = f"https://{provider_base_url}/{provider_api_version}/me"

    if provider_api_version == "v3":
        access_token_method = "PUT"  # nosec

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"Bearer {token.token}"}
        with get_adapter().get_requests_session() as sess:
            response = sess.get(self.profile_url, headers=headers)
            extra_data = response.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(PinterestOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(PinterestOAuth2Adapter)
