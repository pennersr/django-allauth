from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class NetIQOAuth2Adapter(OAuth2Adapter):
    provider_id = "netiq"
    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get("NETIQ_URL")

    @property
    def access_token_url(self):
        return f"{self.provider_base_url}/nidp/oauth/nam/token"

    @property
    def authorize_url(self):
        return f"{self.provider_base_url}/nidp/oauth/nam/authz"

    @property
    def userinfo_url(self):
        return f"{self.provider_base_url}/nidp/oauth/nam/userinfo"

    def complete_login(self, request, app, token, **kwargs):
        """
        Get the user info from userinfo endpoint and return a
        A populated instance of the `SocialLogin` model (unsaved)
        :param request:
        :param app:
        :param token:
        :param kwargs:
        :return:
        """

        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.userinfo_url,
                headers={"Authorization": f"Bearer {token.token}"},
            )
        )

        resp.raise_for_status()
        extra_data = resp.json()
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login


oauth2_login = OAuth2LoginView.adapter_view(NetIQOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(NetIQOAuth2Adapter)
