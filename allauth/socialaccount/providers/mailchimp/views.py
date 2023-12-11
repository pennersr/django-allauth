"""Views for MailChimp API v3."""
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import MailChimpProvider


class MailChimpOAuth2Adapter(OAuth2Adapter):

    """OAuth2Adapter for MailChimp API v3."""

    provider_id = MailChimpProvider.id

    authorize_url = "https://login.mailchimp.com/oauth2/authorize"
    access_token_url = "https://login.mailchimp.com/oauth2/token"
    profile_url = "https://login.mailchimp.com/oauth2/metadata"

    def complete_login(self, request, app, token, **kwargs):
        """Complete login, ensuring correct OAuth header."""
        headers = {"Authorization": "OAuth {0}".format(token.token)}
        metadata = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )
        extra_data = metadata.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(MailChimpOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MailChimpOAuth2Adapter)
