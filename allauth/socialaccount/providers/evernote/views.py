from __future__ import absolute_import

from django.core.urlresolvers import reverse

from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.providers.oauth.client import OAuthError
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialToken, SocialLogin

from ..base import AuthError

import datetime

from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthCallbackView,
                                                         OAuthLoginView)

from .provider import EvernoteProvider


class EvernoteOAuthAdapter(OAuthAdapter):
    provider_id = EvernoteProvider.id
    request_token_url = 'https://sandbox.evernote.com/oauth'
    access_token_url = 'https://sandbox.evernote.com/oauth'
    authorize_url = 'https://sandbox.evernote.com/OAuth.action'

    def complete_login(self, request, app, token, raw_token):
        token.expires_at = datetime.datetime.fromtimestamp(int(raw_token['edam_expires']) / 1000.0)
        extra_data = raw_token
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


class EvernoteOAuthCallbackView(OAuthCallbackView):
    def dispatch(self, request):
        """
        Copies inherited view OAuthCallbackView just to patch a couple items.
        - Fixes blank oauth_token_secret response from Evernote
        - Adds expires_at assignment (by passing raw token response to extra_data)
        """
        login_done_url = reverse(self.adapter.provider_id + "_callback")
        client = self._get_client(request, login_done_url)
        if not client.is_valid():
            if 'denied' in request.GET:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            extra_context = dict(oauth_client=client)
            return render_authentication_error(
                request,
                self.adapter.provider_id,
                error=error,
                extra_context=extra_context)
        app = self.adapter.get_provider().get_app(request)
        try:
            access_token = client.get_access_token()
            access_token['oauth_token_secret'] = ''  # Evernote returns empty oauth_token_secret= kwarg.
            token = SocialToken(
                app=app,
                token=access_token['oauth_token'],
                token_secret=access_token['oauth_token_secret']
            )
            login = self.adapter.complete_login(request, app, token, access_token)
            login.token = token
            login.state = SocialLogin.unstash_state(request)
            return complete_social_login(request, login)
        except OAuthError as e:
            return render_authentication_error(
                request,
                self.adapter.provider_id,
                exception=e)

oauth_login = OAuthLoginView.adapter_view(EvernoteOAuthAdapter)
oauth_callback = EvernoteOAuthCallbackView.adapter_view(EvernoteOAuthAdapter)