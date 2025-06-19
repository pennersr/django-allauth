from datetime import timedelta
from requests import RequestException
from typing import Dict, Optional

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from allauth.account import app_settings as account_settings
from allauth.account.internal.decorators import login_not_required
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.core.internal.httpkit import add_query_params
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.internal import statekit
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.base import ProviderException
from allauth.socialaccount.providers.base.constants import AuthError
from allauth.socialaccount.providers.base.views import BaseLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error
from allauth.utils import build_absolute_uri, get_request_param


class OAuth2Adapter:
    expires_in_key = "expires_in"
    client_class = OAuth2Client
    supports_state = True
    redirect_uri_protocol: Optional[str] = None
    access_token_method = "POST"  # nosec
    login_cancelled_error = "access_denied"
    scope_delimiter = " "
    basic_auth = False
    headers: Optional[Dict[str, str]] = None

    def __init__(self, request):
        self.request = request
        self.did_fetch_access_token = False

    def get_provider(self):
        return get_adapter(self.request).get_provider(
            self.request, provider=self.provider_id
        )

    def complete_login(self, request, app, token: SocialToken, **kwargs):
        """
        Returns a SocialLogin instance
        """
        raise NotImplementedError

    def get_callback_url(self, request, app):
        callback_url = reverse(self.provider_id + "_callback")
        protocol = self.redirect_uri_protocol
        return build_absolute_uri(request, callback_url, protocol)

    def parse_token(self, data):
        token = SocialToken(token=data["access_token"])
        token.token_secret = data.get("refresh_token", "")
        expires_in = data.get(self.expires_in_key, None)
        if expires_in:
            token.expires_at = timezone.now() + timedelta(seconds=int(expires_in))
        return token

    def get_access_token_data(self, request, app, client, pkce_code_verifier=None):
        code = get_request_param(self.request, "code")
        data = client.get_access_token(code, pkce_code_verifier=pkce_code_verifier)
        self.did_fetch_access_token = True
        return data

    def get_client(self, request, app):
        callback_url = self.get_callback_url(request, app)
        client = self.client_class(
            self.request,
            app.client_id,
            app.secret,
            self.access_token_method,
            self.access_token_url,
            callback_url,
            scope_delimiter=self.scope_delimiter,
            headers=self.headers,
            basic_auth=self.basic_auth,
        )
        return client


class OAuth2View:
    @classmethod
    def adapter_view(cls, adapter):
        @login_not_required
        def view(request, *args, **kwargs):
            self = cls()
            self.request = request
            if not isinstance(adapter, OAuth2Adapter):
                self.adapter = adapter(request)
            else:
                self.adapter = adapter
            try:
                return self.dispatch(request, *args, **kwargs)
            except ImmediateHttpResponse as e:
                return e.response

        return view


class OAuth2LoginView(OAuth2View, BaseLoginView):
    def get_provider(self):
        return self.adapter.get_provider()


class OAuth2CallbackView(OAuth2View):
    def dispatch(self, request, *args, **kwargs):
        provider = self.adapter.get_provider()
        state, resp = self._get_state(request, provider)
        if resp:
            return resp
        if "error" in request.GET or "code" not in request.GET:
            # Distinguish cancel from error
            auth_error = request.GET.get("error", None)
            if auth_error == self.adapter.login_cancelled_error:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            return render_authentication_error(
                request,
                provider,
                error=error,
                extra_context={
                    "state": state,
                    "callback_view": self,
                },
            )
        app = provider.app
        client = self.adapter.get_client(self.request, app)

        try:
            access_token = self.adapter.get_access_token_data(
                request, app, client, pkce_code_verifier=state.get("pkce_code_verifier")
            )
            token = self.adapter.parse_token(access_token)
            if app.pk:
                token.app = app
            login = self.adapter.complete_login(
                request, app, token, response=access_token
            )
            login.token = token
            login.state = state
            return complete_social_login(request, login)
        except (
            PermissionDenied,
            OAuth2Error,
            RequestException,
            ProviderException,
        ) as e:
            return render_authentication_error(
                request, provider, exception=e, extra_context={"state": state}
            )

    def _redirect_strict_samesite(self, request, provider):
        if (
            "_redir" in request.GET
            or settings.SESSION_COOKIE_SAMESITE.lower() != "strict"
            or request.method != "GET"
        ):
            return
        redirect_to = request.get_full_path()
        redirect_to = add_query_params(redirect_to, {"_redir": ""})
        return render(
            request,
            "socialaccount/login_redirect." + account_settings.TEMPLATE_EXTENSION,
            {
                "provider": provider,
                "redirect_to": redirect_to,
            },
        )

    def _get_state(self, request, provider):
        state = None
        state_id = get_request_param(request, "state")
        if self.adapter.supports_state:
            if state_id:
                state = statekit.unstash_state(request, state_id)
        else:
            state = statekit.unstash_last_state(request)
        if state is None:
            resp = self._redirect_strict_samesite(request, provider)
            if resp:
                # 'Strict' is in effect, let's try a redirect and then another
                # shot at finding our state...
                return None, resp
            return None, render_authentication_error(
                request,
                provider,
                extra_context={
                    "state_id": state_id,
                    "callback_view": self,
                },
            )
        return state, None
