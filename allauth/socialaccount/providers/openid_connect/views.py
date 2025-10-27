from django.http import Http404
from django.urls import reverse

from allauth.account.internal.decorators import login_not_required
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.internal import jwtkit
from allauth.socialaccount.models import SocialApp, SocialToken
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.utils import build_absolute_uri


class OpenIDConnectOAuth2Adapter(OAuth2Adapter):
    def __init__(self, request, provider_id):
        self.provider_id = provider_id
        super().__init__(request)

    @property
    def openid_config(self):
        if not hasattr(self, "_openid_config"):
            server_url = self.get_provider().server_url
            resp = get_adapter().get_requests_session().get(server_url)
            resp.raise_for_status()
            self._openid_config = resp.json()
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

    def complete_login(self, request, app, token: SocialToken, **kwargs):
        id_token_str = kwargs["response"].get("id_token")
        fetch_userinfo = app.settings.get("fetch_userinfo", True)
        data = {}
        if fetch_userinfo or (not id_token_str):
            data["userinfo"] = self._fetch_user_info(token.token)
        if id_token_str:
            data["id_token"] = self._decode_id_token(app, id_token_str)
        return self.get_provider().sociallogin_from_response(request, data)

    def _fetch_user_info(self, access_token: str) -> dict:
        response = (
            get_adapter()
            .get_requests_session()
            .get(self.profile_url, headers={"Authorization": "Bearer " + access_token})
        )
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

    def get_callback_url(self, request, app):
        callback_url = reverse(
            "openid_connect_callback", kwargs={"provider_id": self.provider_id}
        )
        protocol = self.redirect_uri_protocol
        return build_absolute_uri(request, callback_url, protocol)


@login_not_required
def login(request, provider_id):
    try:
        view = OAuth2LoginView.adapter_view(
            OpenIDConnectOAuth2Adapter(request, provider_id)
        )
        return view(request)
    except SocialApp.DoesNotExist:
        raise Http404


@login_not_required
def callback(request, provider_id):
    try:
        view = OAuth2CallbackView.adapter_view(
            OpenIDConnectOAuth2Adapter(request, provider_id)
        )
        return view(request)
    except SocialApp.DoesNotExist:
        raise Http404
