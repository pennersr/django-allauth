from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class StocktwitsOAuth2Adapter(OAuth2Adapter):
    provider_id = "stocktwits"
    access_token_url = "https://api.stocktwits.com/api/2/oauth/token"  # nosec
    authorize_url = "https://api.stocktwits.com/api/2/oauth/authorize"
    profile_url = "https://api.stocktwits.com/api/2/streams/user/{user}.json"
    scope_delimiter = ","

    def complete_login(self, request, app, token, **kwargs):
        user_id = kwargs.get("response").get("user_id")
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url.format(user=user_id))
            resp.raise_for_status()
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(StocktwitsOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(StocktwitsOAuth2Adapter)
