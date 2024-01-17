import requests

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import GoogleProvider


CERTS_URL = "https://www.googleapis.com/oauth2/v1/certs"

IDENTITY_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

ACCESS_TOKEN_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("ACCESS_TOKEN_URL", "https://oauth2.googleapis.com/token")
)

AUTHORIZE_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("AUTHORIZE_URL", "https://accounts.google.com/o/oauth2/v2/auth")
)

ID_TOKEN_ISSUER = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("ID_TOKEN_ISSUER", "https://accounts.google.com")
)

FETCH_USERINFO = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("FETCH_USERINFO", False)
)


class GoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = GoogleProvider.id
    access_token_url = ACCESS_TOKEN_URL
    authorize_url = AUTHORIZE_URL
    id_token_issuer = ID_TOKEN_ISSUER
    identity_url = IDENTITY_URL
    fetch_userinfo = FETCH_USERINFO

    def complete_login(self, request, app, token, response, **kwargs):
        try:
            identity_data = jwt.decode(
                response["id_token"],
                # Since the token was received by direct communication
                # protected by TLS between this library and Google, we
                # are allowed to skip checking the token signature
                # according to the OpenID Connect Core 1.0
                # specification.
                # https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
                options={
                    "verify_signature": False,
                    "verify_iss": True,
                    "verify_aud": True,
                    "verify_exp": True,
                },
                issuer=self.id_token_issuer,
                audience=app.client_id,
            )
        except jwt.PyJWTError as e:
            raise OAuth2Error("Invalid id_token") from e

        if self.fetch_userinfo and "picture" not in identity_data:
            resp = (
                get_adapter()
                .get_requests_session()
                .get(
                    self.identity_url,
                    headers={"Authorization": "Bearer {}".format(token)},
                )
            )
            if not resp.ok:
                raise OAuth2Error("Request to user info failed")
            identity_data["picture"] = resp.json()["picture"]

        login = self.get_provider().sociallogin_from_response(request, identity_data)
        return login


oauth2_login = OAuth2LoginView.adapter_view(GoogleOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)


class LoginByTokenView(View):
    def dispatch(self, request):
        self.adapter = get_adapter()
        self.provider = self.adapter.get_provider(request, GoogleProvider.id)
        try:
            return super().dispatch(request)
        except (
            requests.RequestException,
            PermissionDenied,
            jwt.PyJWTError,
        ) as exc:
            return render_authentication_error(request, self.provider, exception=exc)

    def get(self, request):
        # If we leave out get() it will return a response with a 405, but
        # we really want to show an authentication error.
        raise PermissionDenied("405")

    def post(self, request, *args, **kwargs):
        self.check_csrf(request)

        credential = request.POST.get("credential")
        alg, key = self.get_key(credential)
        identity_data = jwt.decode(
            credential,
            key,
            options={
                "verify_signature": True,
                "verify_iss": True,
                "verify_aud": True,
                "verify_exp": True,
            },
            issuer=ID_TOKEN_ISSUER,
            audience=self.provider.app.client_id,
            algorithms=[alg],
        )
        login = self.provider.sociallogin_from_response(request, identity_data)
        return complete_social_login(request, login)

    def check_csrf(self, request):
        csrf_token_cookie = request.COOKIES.get("g_csrf_token")
        if not csrf_token_cookie:
            raise PermissionDenied("No CSRF token in Cookie.")
        csrf_token_body = request.POST.get("g_csrf_token")
        if not csrf_token_body:
            raise PermissionDenied("No CSRF token in post body.")
        if csrf_token_cookie != csrf_token_body:
            raise PermissionDenied("Failed to verify double submit cookie.")

    def get_key(self, credential):
        header = jwt.get_unverified_header(credential)
        # {'alg': 'RS256', 'kid': '0ad1fec78504f447bae65bcf5afaedb65eec9e81', 'typ': 'JWT'}
        kid = header["kid"]
        alg = header["alg"]
        response = get_adapter().get_requests_session().get(CERTS_URL)
        response.raise_for_status()
        jwks = response.json()
        key = jwks.get(kid)
        if not key:
            raise PermissionDenied("invalid 'kid'")
        key = load_pem_x509_certificate(
            key.encode("utf8"), default_backend()
        ).public_key()
        return alg, key


login_by_token = csrf_exempt(LoginByTokenView.as_view())
