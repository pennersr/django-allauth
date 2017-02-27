"""Views for Eventbrite API v3."""
import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import EventbriteProvider


class EventbriteOAuth2Adapter(OAuth2Adapter):

    """OAuth2Adapter for Eventbrite API v3."""

    provider_id = EventbriteProvider.id

    authorize_url = 'https://www.eventbrite.com/oauth/authorize'
    access_token_url = 'https://www.eventbrite.com/oauth/token'
    profile_url = 'https://www.eventbriteapi.com/v3/users/me/'

    def complete_login(self, request, app, token, **kwargs):
        """Complete login."""
        resp = requests.get(self.profile_url, params={'token': token.token})
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(EventbriteOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(EventbriteOAuth2Adapter)
