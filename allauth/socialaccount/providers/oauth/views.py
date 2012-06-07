from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from allauth.utils import get_login_redirect_url
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.socialaccount.providers.oauth.client import (OAuthClient,
                                                          OAuthError)
from allauth.socialaccount.helpers import complete_social_login


class OAuthAdapter(object):

    def get_app(self, request):
        return SocialApp.objects.get_current(self.provider_id)

    def get_user_info(self):
        """
        Should return a triple of (user_id, user fields, extra_data)
        """
        raise NotImplementedError


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
        app = self.adapter.get_app(request)
        client = OAuthClient(request, app.key, app.secret,
                             self.adapter.request_token_url,
                             self.adapter.access_token_url,
                             self.adapter.authorize_url,
                             callback_url)
        return client


class OAuthLoginView(OAuthView):
    def dispatch(self, request):
        callback_url = reverse(self.adapter.provider_id + "_callback")
        client = self._get_client(request, callback_url)
        request.session['next'] = get_login_redirect_url(request)
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
        login_done_url = reverse(self.adapter.provider_id + "_complete")
        client = self._get_client(request, login_done_url)
        if not client.is_valid():
            if request.GET.has_key('denied'):
                return HttpResponseRedirect(reverse('socialaccount_login_cancelled'))
            extra_context = dict(oauth_client=client)
            return render_authentication_error(request, extra_context)
        # We're redirecting to the setup view for this oauth service
        return HttpResponseRedirect(client.callback_url)


class OAuthCompleteView(OAuthView):
    def dispatch(self, request):
        app = self.adapter.get_app(request)
        provider_id = self.adapter.provider_id
        try:
            uid, data, extra_data = self.adapter.get_user_info(request, app)
        except OAuthError:
            return render_authentication_error(request)
        try:
            account = SocialAccount.objects.get(provider=provider_id, uid=uid)
        except SocialAccount.DoesNotExist:
            account = SocialAccount(provider=provider_id, uid=uid)
        account.extra_data = extra_data
        if account.pk:
            account.save()
        return complete_social_login(request, data, account)
