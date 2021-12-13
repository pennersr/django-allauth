import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import PinterestProvider


class PinterestOAuth2Adapter(OAuth2Adapter):
    provider_id = PinterestProvider.id

    provider_default_url = "api.pinterest.com"
    provider_default_api_version = "v1"

    settings = app_settings.PROVIDERS.get(provider_id, {})

    provider_base_url = settings.get("PINTEREST_URL", provider_default_url)
    provider_api_version = settings.get(
        "PINTEREST_VERSION", provider_default_api_version
    )

    access_token_url = "https://{0}/{1}/oauth/token".format(
        provider_base_url, provider_api_version
    )
    authorize_url = "https://{0}/oauth/".format(provider_base_url)
    profile_url = "https://{0}/{1}/me".format(provider_base_url, provider_api_version)

    def complete_login(self, request, app, token, **kwargs):
        response = requests.get(self.profile_url, params={"access_token": token.token})
        extra_data = response.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(PinterestOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(PinterestOAuth2Adapter)
