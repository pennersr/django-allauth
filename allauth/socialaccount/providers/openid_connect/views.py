from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from django.http import Http404, HttpRequest, JsonResponse
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.edit import FormView

from allauth import app_settings as allauth_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal.decorators import login_not_required
from allauth.account.internal.flows.logout import logout as logout_locally
from allauth.account.utils import get_next_redirect_url
from allauth.core.internal.httpkit import add_query_params
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.internal import jwtkit, statekit
from allauth.socialaccount.models import SocialApp, SocialToken
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.socialaccount.providers.openid_connect import _sessions
from allauth.socialaccount.providers.openid_connect.forms import BackchannelLogoutForm
from allauth.utils import build_absolute_uri


if TYPE_CHECKING:
    from allauth.socialaccount.providers.openid_connect.provider import (
        OpenIDConnectProvider,
    )


class OpenIDConnectOAuth2Adapter(OAuth2Adapter):
    def __init__(self, request: HttpRequest, provider_id) -> None:
        self.provider_id = provider_id
        super().__init__(request)

    @property
    def openid_config(self):
        if not hasattr(self, "_openid_config"):
            provider = self.get_provider()
            server_url = provider.server_url
            with get_adapter().get_requests_session() as sess:
                resp = sess.get(server_url)
                resp.raise_for_status()
                config = resp.json()
            overrides = provider.app.settings.get("openid_configuration_overrides", {})
            config.update(overrides)
            self._openid_config = config
        return self._openid_config

    @property
    def basic_auth(self):
        token_auth_method = self.get_provider().app.settings.get("token_auth_method")
        if token_auth_method:
            return token_auth_method == "client_secret_basic"  # nosec
        methods = self.openid_config.get("token_endpoint_auth_methods_supported", [])
        # Basic auth is problematic, especially when client ID contains a colon.
        return "client_secret_post" not in methods and "client_secret_basic" in methods

    @property
    def access_token_url(self):
        return self.openid_config["token_endpoint"]

    @property
    def authorize_url(self):
        return self.openid_config["authorization_endpoint"]

    @property
    def profile_url(self):
        return self.openid_config["userinfo_endpoint"]

    def complete_login(self, request: HttpRequest, app, token: SocialToken, **kwargs):
        id_token_str = kwargs["response"].get("id_token")
        fetch_userinfo = app.settings.get("fetch_userinfo", True)
        data = {}
        if fetch_userinfo or (not id_token_str):
            data["userinfo"] = self._fetch_user_info(token.token)
        if id_token_str:
            data["id_token"] = self._decode_id_token(app, id_token_str)
        login = self.get_provider().sociallogin_from_response(request, data)
        if id_token_str:
            login.state["id_token"] = id_token_str
        return login

    def _fetch_user_info(self, access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        with get_adapter().get_requests_session() as sess:
            response = sess.get(self.profile_url, headers=headers)
            response.raise_for_status()
        return response.json()

    def _decode_id_token(self, app: SocialApp, id_token: str) -> dict:
        """
        If the token was received by direct communication protected by
        TLS between this library and Google, we are allowed to skip checking the
        token signature according to the OpenID Connect Core 1.0 specification.

        https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
        """
        verify_signature = not self.did_fetch_access_token
        return jwtkit.verify_and_decode(
            credential=id_token,
            keys_url=self.openid_config["jwks_uri"],
            issuer=self.openid_config["issuer"],
            audience=app.client_id,
            lookup_kid=jwtkit.lookup_kid_jwk,
            verify_signature=verify_signature,
        )

    def get_callback_url(self, request: HttpRequest, app):
        callback_url = reverse(
            "openid_connect_callback", kwargs={"provider_id": self.provider_id}
        )
        protocol = self.redirect_uri_protocol
        return build_absolute_uri(request, callback_url, protocol)


def _get_provider_adapter_or_404(
    request: HttpRequest, provider_id: str
) -> tuple[OpenIDConnectProvider, OpenIDConnectOAuth2Adapter]:
    try:
        adapter = OpenIDConnectOAuth2Adapter(request, provider_id)
        provider = adapter.get_provider()
    except SocialApp.DoesNotExist:
        raise Http404
    return provider, adapter


@login_not_required
def login(request: HttpRequest, provider_id):
    _, adapter = _get_provider_adapter_or_404(request, provider_id)
    view = OAuth2LoginView.adapter_view(adapter)
    return view(request)


@login_not_required
def callback(request: HttpRequest, provider_id):
    _, adapter = _get_provider_adapter_or_404(request, provider_id)
    view = OAuth2CallbackView.adapter_view(adapter)
    return view(request)


@method_decorator(login_not_required, name="dispatch")
class LogoutView(View):
    http_method_names = ["post"]

    def post(self, request: HttpRequest, provider_id: str) -> HttpResponse:
        provider, adapter = _get_provider_adapter_or_404(request, provider_id)
        end_session_endpoint = adapter.openid_config.get("end_session_endpoint")
        next_url = get_next_redirect_url(request)
        if not next_url:
            next_url = get_account_adapter(request).get_logout_redirect_url(request)
        session_data = _sessions.get_session_data(
            request, provider_id=provider.app.provider_id
        )
        id_token = session_data.get("id_token") if session_data else None

        logout_locally(request, show_message=not end_session_endpoint)
        if not end_session_endpoint:
            return HttpResponseRedirect(next_url)

        callback_url = build_absolute_uri(
            request,
            reverse(
                "openid_connect_logout_callback",
                kwargs={"provider_id": provider.app.provider_id},
            ),
        )
        state = statekit.stash_state(
            request,
            provider_id=provider.app.provider_id,
            state={"next": next_url},
        )
        params = {
            "client_id": provider.app.client_id,
            "post_logout_redirect_uri": callback_url,
            "state": state,
        }
        if isinstance(id_token, str):
            params["id_token_hint"] = id_token
        return HttpResponseRedirect(add_query_params(end_session_endpoint, params))


logout = LogoutView.as_view()


@method_decorator(login_not_required, name="dispatch")
class LogoutCallbackView(View):
    def get(self, request: HttpRequest, provider_id: str) -> HttpResponse:
        if not (
            state := statekit.unstash_state(
                request,
                provider_id=provider_id,
                state_id=request.GET.get("state", ""),
            )
        ) or not (redirect_url := state.get("next")):
            redirect_url = get_account_adapter(request).get_logout_redirect_url(request)
        return HttpResponseRedirect(redirect_url)


logout_callback = LogoutCallbackView.as_view()


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(login_not_required, name="dispatch")
# The RP's response SHOULD include the Cache-Control HTTP response header field
# with a no-store value, keeping the response from being cached to prevent
# cached responses from interfering with future logout requests.
@method_decorator(never_cache, name="dispatch")
class BackchannelLogoutView(FormView):
    form_class = BackchannelLogoutForm
    http_method_names = ["post"]

    def dispatch(self, request: HttpRequest, provider_id: str):
        if not allauth_settings.USERSESSIONS_ENABLED:
            return self._failure_response(
                "Improperly configured: `allauth.usersessions` must be enabled."
            )
        self.provider, self.adapter = _get_provider_adapter_or_404(request, provider_id)
        if self.provider.app.settings.get("uid_field", "sub") != "sub":
            return self._failure_response(
                "Improperly configured: `uid_field` must equal `sub`."
            )
        return super().dispatch(request, provider_id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(adapter=self.adapter, provider=self.provider)
        return kwargs

    def form_valid(self, form):
        _sessions.end_sessions(
            self.request,
            provider_id=self.kwargs["provider_id"],
            logout_data=form.logout_data,
        )
        return HttpResponse()

    def form_invalid(self, form):
        description = next(iter(form.errors.values()))[0]
        return self._failure_response(description)

    def _failure_response(self, description: str) -> JsonResponse:
        """
        If the logout request was invalid or the logout failed, the RP MUST
        respond with HTTP 400 Bad Request. The response MAY include an HTTP body
        consisting of a JSON object with error and error_description parameters
        conveying the nature of the error that occurred, which can assist with
        debugging.
        """
        return JsonResponse(
            {
                "error": "invalid_request",
                "error_description": description,
            },
            status=HTTPStatus.BAD_REQUEST,
        )


backchannel_logout = BackchannelLogoutView.as_view()
