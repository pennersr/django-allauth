import hashlib
import hmac
import logging
import requests
from datetime import timedelta

from django import forms
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.views.generic import View

from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .forms import FacebookConnectForm
from .provider import GRAPH_API_URL, GRAPH_API_VERSION, FacebookProvider


logger = logging.getLogger(__name__)


def compute_appsecret_proof(app, token):
    # Generate an appsecret_proof parameter to secure the Graph API call
    # see https://developers.facebook.com/docs/graph-api/securing-requests
    msg = token.token.encode("utf-8")
    key = app.secret.encode("utf-8")
    appsecret_proof = hmac.new(key, msg, digestmod=hashlib.sha256).hexdigest()
    return appsecret_proof


def fb_complete_login(request, app, token):
    provider = app.get_provider(request)
    resp = (
        get_adapter()
        .get_requests_session()
        .get(
            GRAPH_API_URL + "/me",
            params={
                "fields": ",".join(provider.get_fields()),
                "access_token": token.token,
                "appsecret_proof": compute_appsecret_proof(app, token),
            },
        )
    )
    resp.raise_for_status()
    extra_data = resp.json()
    login = provider.sociallogin_from_response(request, extra_data)
    return login


class FacebookOAuth2Adapter(OAuth2Adapter):
    provider_id = FacebookProvider.id
    provider_default_auth_url = "https://www.facebook.com/{}/dialog/oauth".format(
        GRAPH_API_VERSION
    )

    settings = app_settings.PROVIDERS.get(provider_id, {})
    scope_delimiter = ","
    authorize_url = settings.get("AUTHORIZE_URL", provider_default_auth_url)
    access_token_url = GRAPH_API_URL + "/oauth/access_token"
    access_token_method = "GET"
    expires_in_key = "expires_in"

    def complete_login(self, request, app, access_token, **kwargs):
        return fb_complete_login(request, app, access_token)


oauth2_login = OAuth2LoginView.adapter_view(FacebookOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FacebookOAuth2Adapter)


class LoginByTokenView(View):
    def dispatch(self, request):
        try:
            return super().dispatch(request)
        except (
            requests.RequestException,
            forms.ValidationError,
            PermissionDenied,
        ) as exc:
            return render_authentication_error(
                request, FacebookProvider.id, exception=exc
            )

    def get(self, request):
        # If we leave out get().get() it will return a response with a 405, but
        # we really want to show an authentication error.
        raise PermissionDenied("405")

    def post(self, request):
        form = FacebookConnectForm(request.POST)
        if not form.is_valid():
            raise forms.ValidationError()

        adapter = get_adapter()
        provider = adapter.get_provider(request, FacebookProvider.id)
        login_options = provider.get_fb_login_options(request)
        app = provider.app
        access_token = form.cleaned_data["access_token"]

        self.inspect_token(provider, access_token)

        expires_at = None
        if login_options.get("auth_type") == "reauthenticate":
            info = (
                get_adapter()
                .get_requests_session()
                .get(
                    GRAPH_API_URL + "/oauth/access_token_info",
                    params={
                        "client_id": app.client_id,
                        "access_token": access_token,
                    },
                )
                .json()
            )
            nonce = provider.get_nonce(request, pop=True)
            ok = nonce and nonce == info.get("auth_nonce")
        else:
            ok = True
        if ok and provider.get_settings().get("EXCHANGE_TOKEN"):
            resp = (
                get_adapter()
                .get_requests_session()
                .get(
                    GRAPH_API_URL + "/oauth/access_token",
                    params={
                        "grant_type": "fb_exchange_token",
                        "client_id": app.client_id,
                        "client_secret": app.secret,
                        "fb_exchange_token": access_token,
                    },
                )
                .json()
            )
            access_token = resp["access_token"]
            expires_in = resp.get("expires_in")
            if expires_in:
                expires_at = timezone.now() + timedelta(seconds=int(expires_in))
        if ok:
            token = SocialToken(app=app, token=access_token, expires_at=expires_at)
            login = fb_complete_login(request, app, token)
            login.token = token
            login.state = SocialLogin.state_from_request(request)
            ret = complete_social_login(request, login)
        return ret

    def get_app_token(self, provider):
        app = provider.app
        cache_key = f"allauth.facebook.app_token[{app.client_id}]"
        app_token = cache.get(cache_key)
        if not app_token:
            resp = (
                get_adapter()
                .get_requests_session()
                .get(
                    GRAPH_API_URL + "/oauth/access_token",
                    params={
                        "client_id": app.client_id,
                        "client_secret": app.secret,
                        "grant_type": "client_credentials",
                    },
                )
            )
            resp.raise_for_status()
            data = resp.json()
            app_token = data["access_token"]
            timeout = provider.get_settings().get("APP_TOKEN_CACHE_TIMEOUT", 300)
            cache.set(cache_key, app_token, timeout=timeout)
        return app_token

    def inspect_token(self, provider, input_token):
        app_token = self.get_app_token(provider)
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                GRAPH_API_URL + "/debug_token",
                params={"input_token": input_token, "access_token": app_token},
            )
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        if not data["is_valid"]:
            raise PermissionDenied("token is not valid")
        if data["app_id"] != provider.app.client_id or not data["is_valid"]:
            raise PermissionDenied("token app_id mismatch")


login_by_token = LoginByTokenView.as_view()
