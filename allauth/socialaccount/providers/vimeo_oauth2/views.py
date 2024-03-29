"""
Views for PatreonProvider
https://www.patreon.com/platform/documentation/oauth
"""

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class VimeoOAuth2Adapter(OAuth2Adapter):
    provider_id = "vimeo_oauth2"
    access_token_url = "https://api.vimeo.com/oauth/access_token"
    authorize_url = "https://api.vimeo.com/oauth/authorize"
    profile_url = "https://api.vimeo.com/me/"

    def complete_login(self, request, app, token, **kwargs):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.profile_url,
                headers={"Authorization": "Bearer " + token.token},
            )
        )
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(VimeoOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(VimeoOAuth2Adapter)
