from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class TumblrOAuth2Adapter(OAuth2Adapter):
    provider_id = "tumblr_oauth2"
    access_token_url = "https://api.tumblr.com/v2/oauth2/token"  # nosec: B105
    authorize_url = "https://www.tumblr.com/oauth2/authorize"
    profile_url = "https://api.tumblr.com/v2/user/info"

    def complete_login(self, request, app, token, response):
        extra_data = self.get_user_info(token)
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def get_user_info(self, token):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.profile_url,
                headers={"Authorization": "Bearer " + token.token},
            )
        )
        resp.raise_for_status()
        extra_data = resp.json()["response"]["user"]
        return extra_data


oauth2_login = OAuth2LoginView.adapter_view(TumblrOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(TumblrOAuth2Adapter)
