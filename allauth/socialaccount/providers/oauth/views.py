from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.http import urlencode

from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.providers.oauth.client import (OAuthClient,
                                                          OAuthError)
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialToken, SocialLogin

class OAuthAdapter(object):

    def complete_login(self, request, app):
        """
        Returns a SocialLogin instance
        """
        raise NotImplementedError

    def get_provider(self):
        return providers.registry.by_id(self.provider_id)


class OAuthView(object):
    @classmethod
    def adapter_view(cls, adapter):
        def view(request, *args, **kwargs):
            self = cls()
            self.request = request
            self.adapter = adapter()
            return self.dispatch(request, *args, **kwargs)
        return view

    def _get_client(self, request, callback_url):
        app = self.adapter.get_provider().get_app(request)
        client = OAuthClient(request, app.key, app.secret,
                             self.adapter.request_token_url,
                             self.adapter.access_token_url,
                             self.adapter.authorize_url,
                             callback_url)
        return client


class OAuthLoginView(OAuthView):
    def dispatch(self, request):
        callback_url = reverse(self.adapter.provider_id + "_callback")
        # TODO: Can't this be moved as query param into callback?
        # Tried but failed somehow, needs further study...
        request.session['oauth_login_state'] \
            = SocialLogin.marshall_state(request)
        client = self._get_client(request, callback_url)
        try:
            return client.get_redirect()
        except OAuthError:
            return render_authentication_error(request)


class OAuthCallbackView(OAuthView):
    def dispatch(self, request):
        """
        View to handle final steps of OAuth based authentication where the user
        gets redirected back to from the service provider
        """
        login_done_url = reverse(self.adapter.provider_id + "_callback")
        client = self._get_client(request, login_done_url)
        if not client.is_valid():
            if request.GET.has_key('denied'):
                return HttpResponseRedirect(reverse('socialaccount_login_cancelled'))
            extra_context = dict(oauth_client=client)
            return render_authentication_error(request, extra_context)
        app = self.adapter.get_provider().get_app(request)
        try:
            access_token = client.get_access_token()
            token = SocialToken(app=app,
                                token=access_token['oauth_token'],
                                token_secret=access_token['oauth_token_secret'])
            login = self.adapter.complete_login(request, app, token)
            token.account = login.account
            login.token = token
            login.state = SocialLogin.unmarshall_state \
                (request.session.pop('oauth_login_state', None))
            return complete_social_login(request, login)
        except OAuthError:
            return render_authentication_error(request)
