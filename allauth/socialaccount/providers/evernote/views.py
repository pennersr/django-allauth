from __future__ import absolute_import

from datetime import datetime

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthCallbackView,
    OAuthLoginView,
)

from .provider import EvernoteProvider


class EvernoteOAuthAdapter(OAuthAdapter):
    provider_id = EvernoteProvider.id
    settings = app_settings.PROVIDERS.get(provider_id, {})
    request_token_url = 'https://%s/oauth' % (settings.get(
        'EVERNOTE_HOSTNAME',
        'sandbox.evernote.com'))
    access_token_url = 'https://%s/oauth' % (settings.get(
        'EVERNOTE_HOSTNAME',
        'sandbox.evernote.com'))
    authorize_url = 'https://%s/OAuth.action' % (settings.get(
        'EVERNOTE_HOSTNAME',
        'sandbox.evernote.com'))

    def complete_login(self, request, app, token, response):
        token.expires_at = datetime.fromtimestamp(
            int(response['edam_expires']) / 1000.0)
        extra_data = response
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth_login = OAuthLoginView.adapter_view(EvernoteOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(EvernoteOAuthAdapter)
