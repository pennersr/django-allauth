import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import DjOAuthToolkitProvider


class DjOAuthToolkitOAuth2Adapter(OAuth2Adapter):
    provider_id = DjOAuthToolkitProvider.id
    settings = app_settings.PROVIDERS.get(provider_id, {})

    base_url = settings.get("SERVER_URL", "").rstrip("/")
    access_token_url = "%s/oauth/token/" % base_url
    authorize_url = "%s/auth/authorize" % base_url
    profile_url = "%s/oauth/userinfo" % base_url

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.profile_url,
            params={"access_token": token.token},
        )
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(DjOAuthToolkitOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(DjOAuthToolkitOAuth2Adapter)
