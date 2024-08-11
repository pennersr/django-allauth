from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class LemonLDAPOAuth2Adapter(OAuth2Adapter):
    provider_id = "lemonldap"

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get("LEMONLDAP_URL")

    access_token_url = "{0}/oauth2/token".format(provider_base_url)
    authorize_url = "{0}/oauth2/authorize".format(provider_base_url)
    profile_url = "{0}/oauth2/userinfo".format(provider_base_url)

    def complete_login(self, request, app, token: SocialToken, **kwargs):
        response = (
            get_adapter()
            .get_requests_session()
            .post(self.profile_url, headers={"Authorization": "Bearer " + token.token})
        )
        response.raise_for_status()
        extra_data = response.json()
        extra_data["id"] = extra_data["sub"]
        del extra_data["sub"]

        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(LemonLDAPOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(LemonLDAPOAuth2Adapter)
