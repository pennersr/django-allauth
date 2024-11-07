from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class FoursquareOAuth2Adapter(OAuth2Adapter):
    provider_id = "foursquare"
    access_token_url = "https://foursquare.com/oauth2/access_token"  # nosec
    # Issue ?? -- this one authenticates over and over again...
    # authorize_url = 'https://foursquare.com/oauth2/authorize'
    authorize_url = "https://foursquare.com/oauth2/authenticate"
    profile_url = "https://api.foursquare.com/v2/users/self"

    def complete_login(self, request, app, token, **kwargs):
        # Foursquare needs a version number for their API requests as
        # documented here
        # https://developer.foursquare.com/overview/versioning
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.profile_url,
                params={"oauth_token": token.token, "v": "20140116"},
            )
        )
        extra_data = resp.json()["response"]["user"]
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FoursquareOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FoursquareOAuth2Adapter)
