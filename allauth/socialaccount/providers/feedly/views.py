from __future__ import unicode_literals

from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import FeedlyProvider


class FeedlyOAuth2Adapter(OAuth2Adapter):
    provider_id = FeedlyProvider.id
    host = app_settings.PROVIDERS.get(provider_id, {}).get("HOST", "cloud.feedly.com")
    access_token_url = "https://%s/v3/auth/token" % host
    authorize_url = "https://%s/v3/auth/auth" % host
    profile_url = "https://%s/v3/profile" % host

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "OAuth {0}".format(token.token)}
        resp = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FeedlyOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FeedlyOAuth2Adapter)
