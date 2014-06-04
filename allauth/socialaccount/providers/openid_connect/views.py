from __future__ import absolute_import

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.openid_connect.client import OpenidConnectClient
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2View, OAuth2LoginView, OAuth2CallbackView
from allauth.socialaccount.models import SocialToken, SocialLogin
from allauth.socialaccount.helpers import complete_social_login

from django.core.urlresolvers import reverse
from allauth.utils import build_absolute_uri


class OpenidConnectAdapter(OAuth2Adapter):
    pass


class OpenidConnectView(OAuth2View):

    def get_client(self, request, app):
        callback_url = reverse(self.adapter.provider_id + "_callback")
        callback_url = build_absolute_uri(
            request, callback_url,
            protocol=self.adapter.redirect_uri_protocol)
        provider = self.adapter.get_provider()
        client = OpenidConnectClient(self.request, app.client_id, app.secret,
                              self.adapter.access_token_method,
                              self.adapter.access_token_url,
                              callback_url,
                              self.adapter.open_id_url,
                              provider.get_scope())
        return client


class OpenidConnectLoginView(OAuth2LoginView):
    pass


class OpenidConnectCallbackView(OpenidConnectView):
    def dispatch(self, request):
        if 'error' in request.GET or not 'code' in request.GET:
            # TODO: Distinguish cancel from error
            return render_authentication_error(request)
        app = self.adapter.get_provider().get_app(self.request)
        client = self.get_client(request, app)
        try:
            access_token = client.get_access_token(request.GET['code'])
            token = self.adapter.parse_token(access_token)
            token.app = app
            # jp 6/1/2014 get open id from qq using the access token
            open_id = client.get_open_id(token.token)

            login = self.adapter.complete_login(request,
                                                app,
                                                token,
                                                response=access_token,
                                                consumer_key=client.consumer_key,
                                                openid=open_id)
            token.account = login.account
            login.token = token
            if self.adapter.supports_state:
                login.state = SocialLogin \
                    .verify_and_unstash_state(
                        request,
                        request.REQUEST.get('state'))
            else:
                login.state = SocialLogin.unstash_state(request)
            return complete_social_login(request, login)
        except OAuth2Error as e:
            return render_authentication_error(request)
