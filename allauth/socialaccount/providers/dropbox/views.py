from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class DropboxOAuth2Adapter(OAuth2Adapter):
    provider_id = "dropbox"
    access_token_url = "https://api.dropbox.com/oauth2/token"  # nosec
    authorize_url = "https://www.dropbox.com/oauth2/authorize"
    profile_url = "https://api.dropbox.com/2/users/get_current_account"

    def complete_login(self, request, app, token, **kwargs):
        response = (
            get_adapter()
            .get_requests_session()
            .post(
                self.profile_url,
                headers={"Authorization": "Bearer %s" % (token.token,)},
            )
        )
        response.raise_for_status()
        return self.get_provider().sociallogin_from_response(request, response.json())


oauth_login = OAuth2LoginView.adapter_view(DropboxOAuth2Adapter)
oauth_callback = OAuth2CallbackView.adapter_view(DropboxOAuth2Adapter)
