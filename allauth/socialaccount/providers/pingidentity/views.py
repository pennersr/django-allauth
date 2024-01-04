from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import PingIdentityProvider


class PingIdentityAdapter(OAuth2Adapter):
    provider_id = PingIdentityProvider.id

    settings = app_settings.PROVIDERS.get(provider_id, {})
    ping_base_url = settings.get("PING_BASE_URL")

    @property
    def access_token_url(self):
        return "https://{}/as/token.oauth2".format(self.ping_base_url)

    @property
    def authorize_url(self):
        return "https://{}/as/authorization.oauth2".format(self.ping_base_url)

    @property
    def userinfo_url(self):
        return "https://{}/idp/userinfo.openid".format(self.ping_base_url)

    @property
    def access_token_method(self):
        return "POST"

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
                headers={"Authorization": "Bearer {}".format(token.token)},
            )
        )

        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(PingIdentityAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(PingIdentityAdapter)
