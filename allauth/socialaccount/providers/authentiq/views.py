from urllib.parse import urljoin

from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class AuthentiqOAuth2Adapter(OAuth2Adapter):
    provider_id = "authentiq"

    settings = app_settings.PROVIDERS.get(provider_id, {})

    provider_url = settings.get("PROVIDER_URL", "https://connect.authentiq.io/")
    if not provider_url.endswith("/"):
        provider_url += "/"

    access_token_url = urljoin(provider_url, "token")
    authorize_url = urljoin(provider_url, "authorize")
    profile_url = urljoin(provider_url, "userinfo")

    def complete_login(self, request, app, token, **kwargs):
        auth = {"Authorization": "Bearer " + token.token}
        resp = get_adapter().get_requests_session().get(self.profile_url, headers=auth)
        resp.raise_for_status()
        extra_data = resp.json()
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login


oauth2_login = OAuth2LoginView.adapter_view(AuthentiqOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AuthentiqOAuth2Adapter)
