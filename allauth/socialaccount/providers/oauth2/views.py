from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from allauth.utils import get_login_redirect_url
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.socialaccount import providers
from allauth.socialaccount.providers.oauth2.client import (OAuth2Client,
                                                           OAuth2Error)
from allauth.socialaccount.helpers import complete_social_login


class OAuth2Adapter(object):

    def get_provider(self):
        return providers.registry.by_id(self.provider_id)

    def get_app(self, request):
        return SocialApp.objects.get_current(self.provider_id)

    def get_user_info(self):
        """
        Should return a triple of (user_id, user fields, extra_data)
        """
        raise NotImplementedError

class OAuth2View(object):
    @classmethod
    def adapter_view(cls, adapter):
        def view(request, *args, **kwargs):
            self = cls()
            self.request = request
            self.adapter = adapter()
            return self.dispatch(request, *args, **kwargs)
        return view

    def get_client(self, request, app):
        callback_url = reverse(self.adapter.provider_id + "_complete")
        callback_url = request.build_absolute_uri(callback_url)
        client = OAuth2Client(self.request, app.key, app.secret,
                              self.adapter.authorize_url,
                              self.adapter.access_token_url,
                              callback_url,
                              self.adapter.get_provider().get_scope())
        return client


class OAuth2LoginView(OAuth2View):
    def dispatch(self, request):
        app = self.adapter.get_app(self.request)
        client = self.get_client(request, app)
        # TODO: next can be passed along to callback url, session not required
        request.session['next'] = get_login_redirect_url(request)
        try:
            return HttpResponseRedirect(client.get_redirect_url())
        except OAuth2Error:
            return render_authentication_error(request)


class OAuth2CompleteView(OAuth2View):
    def dispatch(self, request):
        if 'error' in request.GET or not 'code' in request.GET:
            # TODO: Distinguish cancel from error
            return render_authentication_error(request)
        app = self.adapter.get_app(self.request)
        client = self.get_client(request, app)
        provider_id = self.adapter.provider_id
        try:
            access_token = client.get_access_token(request.GET['code'])
            uid, data, extra_data = self.adapter.get_user_info(request,
                                                               app,
                                                               access_token)
        except OAuth2Error:
            return render_authentication_error(request)
        # TODO: DRY, duplicates OAuth logic
        try:
            account = SocialAccount.objects.get(provider=provider_id, uid=uid)
        except SocialAccount.DoesNotExist:
            account = SocialAccount(provider=provider_id, uid=uid)
        account.extra_data = extra_data
        if account.pk:
            account.save()
        return complete_social_login(request, data, account)
