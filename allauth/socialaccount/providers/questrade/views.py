from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class QuestradeOAuth2Adapter(OAuth2Adapter):
    provider_id = "questrade"
    access_token_url = "https://login.questrade.com/oauth2/token"  # nosec
    authorize_url = "https://login.questrade.com/oauth2/authorize"
    supports_state = False

    def complete_login(self, request, app, token, **kwargs):
        api_server = kwargs.get("response", {}).get(
            "api_server", "https://api01.iq.questrade.com/"
        )
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                "{}v1/accounts".format(api_server),
                headers={"Authorization": "Bearer {}".format(token.token)},
            )
        )
        resp.raise_for_status()
        data = resp.json()
        data.update(kwargs)
        return self.get_provider().sociallogin_from_response(request, data)


oauth2_login = OAuth2LoginView.adapter_view(QuestradeOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(QuestradeOAuth2Adapter)
