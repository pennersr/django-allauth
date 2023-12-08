from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import TwitterOAuth2Provider


class TwitterOAuth2Adapter(OAuth2Adapter):
    provider_id = TwitterOAuth2Provider.id
    access_token_url = "https://api.twitter.com/2/oauth2/token"
    authorize_url = "https://twitter.com/i/oauth2/authorize"
    profile_url = "https://api.twitter.com/2/users/me"
    basic_auth = True

    def complete_login(self, request, app, access_token, **kwargs):
        extra_data = self.get_user_info(access_token)
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def get_user_info(self, token):
        fields = self.get_provider().get_fields()
        headers = {}
        headers.update(self.get_provider().get_settings().get("HEADERS", {}))
        headers["Authorization"] = " ".join(["Bearer", token.token])

        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                url=self.profile_url,
                params={"user.fields": ",".join(fields)},
                headers=headers,
            )
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        return data


oauth2_login = OAuth2LoginView.adapter_view(TwitterOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(TwitterOAuth2Adapter)
