#===============================================================================
# Support for Reddit Oauth2 authentication
# Author: Wendy Edwards (wayward710)
#===============================================================================

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView,
                                                          OAuth2View)
from allauth.socialaccount.providers.reddit_oauth2.client import RedditOauth2Client
import requests
from django.core.urlresolvers import reverse
from allauth.utils import build_absolute_uri
from allauth.account import app_settings
from .provider import RedditOAuth2Provider
from django.http import HttpResponseRedirect
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.models import SocialToken, SocialLogin
from allauth.socialaccount.providers.oauth2.client import (OAuth2Client,
                                                           OAuth2Error)
from allauth.utils import get_request_param
from allauth.socialaccount.helpers import complete_social_login
from django.core.exceptions import PermissionDenied
from ..base import AuthAction, AuthError

# Standard Reddit Oauth2 URLs
class RedditOAuth2Adapter(OAuth2Adapter):
    provider_id = RedditOAuth2Provider.id
    access_token_url = 'https://www.reddit.com/api/v1/access_token'
    authorize_url = 'https://www.reddit.com/api/v1/authorize'
    profile_url = 'https://oauth.reddit.com/api/v1/me'

    # After successfully logging in, use access token to retrieve user info
    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "bearer " + token.token,
            "User-Agent": "django-allauth-header"}
        extra_data = requests.get(self.profile_url, headers=headers)

        # This only here because of weird response from the test suite
        if isinstance(extra_data, list):
            extra_data = extra_data[0]

        return self.get_provider().sociallogin_from_response(
            request,
            extra_data.json()
        )

# Use RedditOauth2Client instead of default Oauth2 client
class RedditOauth2View(OAuth2View):
    def get_client(self, request, app):
        callback_url = reverse(self.adapter.provider_id + "_callback")
        protocol = (self.adapter.redirect_uri_protocol
                    or app_settings.DEFAULT_HTTP_PROTOCOL)
        callback_url = build_absolute_uri(
            request, callback_url,
            protocol=protocol)
        provider = self.adapter.get_provider()
        scope = provider.get_scope(request)
        client = RedditOauth2Client(self.request, app.client_id, app.secret,
                              self.adapter.access_token_method,
                              self.adapter.access_token_url,
                              callback_url,
                              scope)
        return client    
    
class RedditOAuth2LoginView(RedditOauth2View):
    def dispatch(self, request):
        provider = self.adapter.get_provider()
        app = provider.get_app(self.request)
        client = self.get_client(request, app)
        action = request.GET.get('action', AuthAction.AUTHENTICATE)
        auth_url = self.adapter.authorize_url
        auth_params = provider.get_auth_params(request, action)
        client.state = SocialLogin.stash_state(request)
        try:
            return HttpResponseRedirect(client.get_redirect_url(
                auth_url, auth_params))
        except OAuth2Error as e:
            return render_authentication_error(
                request,
                provider.id,
                exception=e)
            
class RedditOAuth2CallbackView(RedditOauth2View):
    def dispatch(self, request):
        if 'error' in request.GET or 'code' not in request.GET:
            # Distinguish cancel from error
            auth_error = request.GET.get('error', None)
            if auth_error == self.adapter.login_cancelled_error:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            return render_authentication_error(
                request,
                self.adapter.provider_id,
                error=error)
        app = self.adapter.get_provider().get_app(self.request)
        client = self.get_client(request, app)
        try:
            access_token = client.get_access_token(request.GET['code'])
            token = self.adapter.parse_token(access_token)
            token.app = app
            login = self.adapter.complete_login(request,
                                                app,
                                                token,
                                                response=access_token)
            login.token = token
            if self.adapter.supports_state:
                login.state = SocialLogin \
                    .verify_and_unstash_state(
                        request,
                        get_request_param(request, 'state'))
            else:
                login.state = SocialLogin.unstash_state(request)
            return complete_social_login(request, login)
        except (PermissionDenied, OAuth2Error) as e:
            return render_authentication_error(
                request,
                self.adapter.provider_id,
                exception=e)            
             
# We need to use our classes here, not the default Oauth2 ones                
oauth_login = RedditOAuth2LoginView.adapter_view(RedditOAuth2Adapter)
oauth_callback = RedditOAuth2CallbackView.adapter_view(RedditOAuth2Adapter)
