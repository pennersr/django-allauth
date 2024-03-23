import requests

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.internal import jwtkit
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


CERTS_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("CERTS_URL", "https://www.googleapis.com/oauth2/v1/certs")
)

IDENTITY_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("IDENTITY_URL", "https://www.googleapis.com/oauth2/v2/userinfo")
)

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


def _verify_and_decode(app, credential, verify_signature=True):
    return jwtkit.verify_and_decode(
        credential=credential,
        keys_url=CERTS_URL,
        issuer=ID_TOKEN_ISSUER,
        audience=app.client_id,
        lookup_kid=jwtkit.lookup_kid_pem_x509_certificate,
        verify_signature=verify_signature,
    )


class GoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = "google"
    access_token_url = ACCESS_TOKEN_URL
    authorize_url = AUTHORIZE_URL
    id_token_issuer = ID_TOKEN_ISSUER
    identity_url = IDENTITY_URL
    fetch_userinfo = FETCH_USERINFO

    def complete_login(self, request, app, token, response, **kwargs):
        data = None
        id_token = response.get("id_token")
        if id_token:
            data = self._decode_id_token(app, id_token)
            if self.fetch_userinfo and "picture" not in data:
                info = self._fetch_user_info(token.token)
                picture = info.get("picture")
                if picture:
                    data["picture"] = picture
        else:
            data = self._fetch_user_info(token.token)
        login = self.get_provider().sociallogin_from_response(request, data)
        return login

    def _decode_id_token(self, app, id_token):
        """
        If the token was received by direct communication protected by
        TLS between this library and Google, we are allowed to skip checking the
        token signature according to the OpenID Connect Core 1.0 specification.

        https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
        """
        verify_signature = not self.did_fetch_access_token
        return _verify_and_decode(app, id_token, verify_signature=verify_signature)

    def _fetch_user_info(self, access_token):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.identity_url,
                headers={"Authorization": "Bearer {}".format(access_token)},
            )
        )
        if not resp.ok:
            raise OAuth2Error("Request to user info failed")
        return resp.json()


oauth2_login = OAuth2LoginView.adapter_view(GoogleOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)


class LoginByTokenView(View):
    def dispatch(self, request):
        self.adapter = get_adapter()
        self.provider = self.adapter.get_provider(
            request, GoogleOAuth2Adapter.provider_id
        )
        try:
            return super().dispatch(request)
        except (
            OAuth2Error,
            requests.RequestException,
            PermissionDenied,
            ValidationError,
        ) as exc:
            return render_authentication_error(request, self.provider, exception=exc)

    def get(self, request):
        # If we leave out get() it will return a response with a 405, but
        # we really want to show an authentication error.
        raise PermissionDenied("405")

    def post(self, request, *args, **kwargs):
        self.check_csrf(request)

        credential = request.POST.get("credential")
        login = self.provider.verify_token(request, {"id_token": credential})
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


login_by_token = csrf_exempt(LoginByTokenView.as_view())
