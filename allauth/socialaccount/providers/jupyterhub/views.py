from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class JupyterHubOAuth2Adapter(OAuth2Adapter):
    provider_id = "jupyterhub"

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get("API_URL", "")

    access_token_url = "{0}/hub/api/oauth2/token".format(provider_base_url)
    authorize_url = "{0}/hub/api/oauth2/authorize".format(provider_base_url)
    profile_url = "{0}/hub/api/user".format(provider_base_url)

    def complete_login(self, request, app, access_token, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(access_token)}

        extra_data = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )

        user_profile = extra_data.json()

        return self.get_provider().sociallogin_from_response(request, user_profile)


oauth2_login = OAuth2LoginView.adapter_view(JupyterHubOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(JupyterHubOAuth2Adapter)
