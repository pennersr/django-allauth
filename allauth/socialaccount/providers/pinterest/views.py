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
    access_token_url = "https://{0}/{1}/oauth/token".format(
        provider_base_url, provider_api_version
    )
    basic_auth = True
    if provider_api_version == "v5":
        profile_url = "https://{0}/{1}/user_account".format(
            provider_base_url, provider_api_version
        )
    elif provider_api_version == "v3":
        profile_url = "https://{0}/{1}/users/me".format(
            provider_base_url, provider_api_version
        )
    else:
        profile_url = "https://{0}/{1}/me".format(
            provider_base_url, provider_api_version
        )

    if provider_api_version == "v3":
        access_token_method = "PUT"

    def complete_login(self, request, app, token, **kwargs):
        response = (
            get_adapter()
            .get_requests_session()
            .get(self.profile_url, headers={"Authorization": "Bearer " + token.token})
        )
        extra_data = response.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(PinterestOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(PinterestOAuth2Adapter)
