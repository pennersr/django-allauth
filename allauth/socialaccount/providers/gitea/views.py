import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.gitea.provider import GiteaProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class GiteaOAuth2Adapter(OAuth2Adapter):
    provider_id = GiteaProvider.id
    settings = app_settings.PROVIDERS.get(provider_id, {})

    if "GITEA_URL" in settings:
        web_url = settings.get("GITEA_URL").rstrip("/")
        api_url = "{0}/api/v1".format(web_url)
    else:
        web_url = "https://gitea.com"
        api_url = "https://gitea.com"

    access_token_url = "{0}/login/oauth/access_token".format(web_url)
    authorize_url = "{0}/login/oauth/authorize".format(web_url)
    profile_url = "{0}/user".format(api_url)

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "token {}".format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(GiteaOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GiteaOAuth2Adapter)
