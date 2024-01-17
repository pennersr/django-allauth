from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import PaypalProvider


class PaypalOAuth2Adapter(OAuth2Adapter):
    provider_id = PaypalProvider.id
    supports_state = False

    @property
    def authorize_url(self):
        path = "webapps/auth/protocol/openidconnect/v1/authorize"
        return "https://www.{0}/{1}".format(self._get_endpoint(), path)

    @property
    def access_token_url(self):
        path = "v1/identity/openidconnect/tokenservice"
        return "https://api.{0}/{1}".format(self._get_endpoint(), path)

    @property
    def profile_url(self):
        path = "v1/identity/openidconnect/userinfo"
        return "https://api.{0}/{1}".format(self._get_endpoint(), path)

    def _get_endpoint(self):
        settings = self.get_provider().get_settings()
        if settings.get("MODE") == "live":
            return "paypal.com"
        else:
            return "sandbox.paypal.com"

    def complete_login(self, request, app, token, **kwargs):
        response = (
            get_adapter()
            .get_requests_session()
            .post(
                self.profile_url,
                params={"schema": "openid", "access_token": token},
            )
        )
        extra_data = response.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(PaypalOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(PaypalOAuth2Adapter)
