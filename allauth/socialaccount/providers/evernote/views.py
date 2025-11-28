from datetime import datetime

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthCallbackView,
    OAuthLoginView,
)


class EvernoteOAuthAdapter(OAuthAdapter):
    provider_id = "evernote"
    settings = app_settings.PROVIDERS.get(provider_id, {})
    _hostname = settings.get("EVERNOTE_HOSTNAME", "sandbox.evernote.com")
    request_token_url = f"https://{_hostname}/oauth"
    access_token_url = f"https://{_hostname}/oauth"
    authorize_url = f"https://{_hostname}/OAuth.action"
    del _hostname

    def complete_login(self, request, app, token, response):
        token.expires_at = datetime.fromtimestamp(
            int(response["edam_expires"]) / 1000.0
        )
        extra_data = response
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth_login = OAuthLoginView.adapter_view(EvernoteOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(EvernoteOAuthAdapter)
