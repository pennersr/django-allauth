import hashlib
import hmac
from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.socialaccount.providers.base import Provider
from allauth.socialaccount.providers.facebook.constants import GRAPH_API_URL


def compute_appsecret_proof(app, token):
    # Generate an appsecret_proof parameter to secure the Graph API call
    # see https://developers.facebook.com/docs/graph-api/securing-requests
    msg = token.token.encode("utf-8")
    key = app.secret.encode("utf-8")
    appsecret_proof = hmac.new(key, msg, digestmod=hashlib.sha256).hexdigest()
    return appsecret_proof


def complete_login(request, provider, token):
    resp = (
        get_adapter()
        .get_requests_session()
        .get(
            GRAPH_API_URL + "/me",
            params={
                "fields": ",".join(provider.get_fields()),
                "access_token": token.token,
                "appsecret_proof": compute_appsecret_proof(provider.app, token),
            },
        )
    )
    resp.raise_for_status()
    extra_data = resp.json()
    login = provider.sociallogin_from_response(request, extra_data)
    return login


def get_app_token(provider):
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


def inspect_token(provider, input_token):
    app_token = get_app_token(provider)
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
        raise get_adapter().validation_error("invalid_token")
    if data["app_id"] != provider.app.client_id or not data["is_valid"]:
        raise get_adapter().validation_error("invalid_token")


def verify_token(
    request,
    provider: Provider,
    access_token: str,
    auth_type: str = "",
    auth_nonce: str = "",
) -> SocialLogin:
    app = provider.app
    inspect_token(provider, access_token)
    expires_at = None
    if auth_type == "reauthenticate":
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                GRAPH_API_URL + "/oauth/access_token_info",
                params={
                    "client_id": app.client_id,
                    "access_token": access_token,
                },
            )
        )
        resp.raise_for_status()
        info = resp.json()
        ok = auth_nonce and auth_nonce == info.get("auth_nonce")
        if not ok:
            raise get_adapter().validation_error("invalid_token")

    if provider.get_settings().get("EXCHANGE_TOKEN"):
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
        )
        resp.raise_for_status()
        info = resp.json()
        access_token = info["access_token"]
        expires_in = info.get("expires_in")
        if expires_in:
            expires_at = timezone.now() + timedelta(seconds=int(expires_in))

    token = SocialToken(app=app, token=access_token, expires_at=expires_at)
    login = complete_login(request, provider, token)
    login.token = token
    return login
