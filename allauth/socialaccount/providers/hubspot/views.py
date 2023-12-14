"""Views for Hubspot API."""
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import HubspotProvider


class HubspotOAuth2Adapter(OAuth2Adapter):
    """OAuth2Adapter for Hubspot API v3."""

    provider_id = HubspotProvider.id

    authorize_url = "https://app.hubspot.com/oauth/authorize"
    access_token_url = "https://api.hubapi.com/oauth/v1/token"
    profile_url = "https://api.hubapi.com/oauth/v1/access-tokens"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Content-Type": "application/json"}
        response = (
            get_adapter()
            .get_requests_session()
            .get("{0}/{1}".format(self.profile_url, token.token), headers=headers)
        )
        response.raise_for_status()
        extra_data = response.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(HubspotOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(HubspotOAuth2Adapter)
