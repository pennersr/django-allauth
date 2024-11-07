from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class StripeOAuth2Adapter(OAuth2Adapter):
    provider_id = "stripe"
    access_token_url = "https://connect.stripe.com/oauth/token"  # nosec
    authorize_url = "https://connect.stripe.com/oauth/authorize"
    profile_url = "https://api.stripe.com/v1/accounts/%s"

    def complete_login(self, request, app, token, response, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(token.token)}
        resp = (
            get_adapter()
            .get_requests_session()
            .get(self.profile_url % response.get("stripe_user_id"), headers=headers)
        )
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(StripeOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(StripeOAuth2Adapter)
