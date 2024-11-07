from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class BoxOAuth2Adapter(OAuth2Adapter):
    provider_id = "box"
    access_token_url = "https://api.box.com/oauth2/token"  # nosec
    authorize_url = "https://account.box.com/api/oauth2/authorize"
    profile_url = "https://api.box.com/2.0/users/me"
    redirect_uri_protocol = None

    def complete_login(self, request, app, token, **kwargs):
        extra_data = (
            get_adapter()
            .get_requests_session()
            .get(self.profile_url, params={"access_token": token.token})
        )

        # This only here because of weird response from the test suite
        if isinstance(extra_data, list):
            extra_data = extra_data[0]

        return self.get_provider().sociallogin_from_response(request, extra_data.json())


oauth_login = OAuth2LoginView.adapter_view(BoxOAuth2Adapter)
oauth_callback = OAuth2CallbackView.adapter_view(BoxOAuth2Adapter)
