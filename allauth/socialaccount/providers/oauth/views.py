import logging

from django.urls import reverse

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.socialaccount.providers.base.constants import AuthError
from allauth.socialaccount.providers.base.views import BaseLoginView
from allauth.socialaccount.providers.oauth.client import (
    OAuthClient,
    OAuthError,
)


logger = logging.getLogger(__name__)


class OAuthAdapter:
    client_class = OAuthClient

    def __init__(self, request):
        self.request = request

    def complete_login(self, request, app):
        """
        Returns a SocialLogin instance
        """
        raise NotImplementedError

    def get_provider(self):
        adapter = get_adapter(self.request)
        app = adapter.get_app(self.request, provider=self.provider_id)
        return app.get_provider(self.request)

    def _get_client(self, request, callback_url, scope=None):
        provider = self.get_provider()
        app = provider.app
        parameters = {}
        if scope:
            parameters["scope"] = " ".join(scope)
        client = self.client_class(
            request,
            app.client_id,
            app.secret,
            self.request_token_url,
            self.access_token_url,
            callback_url,
            parameters=parameters,
            provider=provider,
        )
        return client


class OAuthView:
    @classmethod
    def adapter_view(cls, adapter):
        def view(request, *args, **kwargs):
            self = cls()
            self.request = request
            self.adapter = adapter(request)
            return self.dispatch(request, *args, **kwargs)

        return view


class OAuthLoginView(OAuthView, BaseLoginView):
    def get_provider(self):
        provider = self.adapter.get_provider()
        return provider


class OAuthCallbackView(OAuthView):
    def dispatch(self, request):
        """
        View to handle final steps of OAuth based authentication where the user
        gets redirected back to from the service provider
        """
        provider = self.adapter.get_provider()
        login_done_url = reverse(self.adapter.provider_id + "_callback")
        client = self.adapter._get_client(request, login_done_url)
        if not client.is_valid():
            if "denied" in request.GET:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            return render_authentication_error(
                request,
                provider,
                error=error,
                extra_context={
                    "oauth_client": client,
                    "callback_view": self,
                },
            )
        app = provider.app
        try:
            access_token = client.get_access_token()
            token = SocialToken(
                app=app,
                token=access_token["oauth_token"],
                # .get() -- e.g. Evernote does not feature a secret
                token_secret=access_token.get("oauth_token_secret", ""),
            )
            login = self.adapter.complete_login(
                request, app, token, response=access_token
            )
            login.token = token
            login.state = SocialLogin.unstash_state(request)
            return complete_social_login(request, login)
        except OAuthError as e:
            return render_authentication_error(request, provider, exception=e)
