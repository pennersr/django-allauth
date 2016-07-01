from __future__ import absolute_import

from django.core.urlresolvers import reverse

from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.providers.oauth.client import (OAuthClient,
                                                          OAuthError)
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialToken, SocialLogin

from ..base import AuthAction, AuthError


class OAuthAdapter(object):

    def __init__(self, request):
        self.request = request

    def complete_login(self, request, app):
        """
        Returns a SocialLogin instance
        """
        raise NotImplementedError

    def get_provider(self):
        return providers.registry.by_id(self.provider_id, self.request)


class OAuthView(object):
    @classmethod
    def adapter_view(cls, adapter):
        def view(request, *args, **kwargs):
            self = cls()
            self.request = request
            self.adapter = adapter(request)
            return self.dispatch(request, *args, **kwargs)
        return view

    def _get_client(self, request, callback_url):
        provider = self.adapter.get_provider()
        app = provider.get_app(request)
        scope = ' '.join(provider.get_scope(request))
        parameters = {}
        if scope:
            parameters['scope'] = scope
        client = OAuthClient(request, app.client_id, app.secret,
                             self.adapter.request_token_url,
                             self.adapter.access_token_url,
                             callback_url,
                             parameters=parameters, provider=provider)
        return client


class OAuthLoginView(OAuthView):
    def dispatch(self, request):
        callback_url = reverse(self.adapter.provider_id + "_callback")
        SocialLogin.stash_state(request)
        action = request.GET.get('action', AuthAction.AUTHENTICATE)
        provider = self.adapter.get_provider()
        auth_url = provider.get_auth_url(request,
                                         action) or self.adapter.authorize_url
        auth_params = provider.get_auth_params(request, action)
        client = self._get_client(request, callback_url)
        try:
            return client.get_redirect(auth_url, auth_params)
        except OAuthError as e:
            return render_authentication_error(request,
                                               self.adapter.provider_id,
                                               exception=e)


class OAuthCallbackView(OAuthView):
    def dispatch(self, request):
        """
        View to handle final steps of OAuth based authentication where the user
        gets redirected back to from the service provider
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
            token = SocialToken(
                app=app,
                token=access_token['oauth_token'],
                # .get() -- e.g. Evernote does not feature a secret
                token_secret=access_token.get('oauth_token_secret', ''))
            login = self.adapter.complete_login(request,
                                                app,
                                                token,
                                                response=access_token)
            login.token = token
            login.state = SocialLogin.unstash_state(request)
            return complete_social_login(request, login)
        except OAuthError as e:
            return render_authentication_error(
                request,
                self.adapter.provider_id,
                exception=e)
