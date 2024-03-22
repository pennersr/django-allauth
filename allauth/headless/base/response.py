from django.http import JsonResponse
from django.utils.cache import add_never_cache_headers

from allauth import app_settings as allauth_app_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.authentication import get_authentication_records
from allauth.account.models import EmailAddress
from allauth.account.utils import user_display, user_username
from allauth.headless.internal import authkit, sessionkit


class APIResponse(JsonResponse):
    def __init__(self, data=None, meta=None, status=200):
        d = {"status": status}
        if data is not None:
            d["data"] = data
        if meta is not None:
            d["meta"] = meta
        super().__init__(d, status=status)
        add_never_cache_headers(self)


class UnauthorizedResponse(APIResponse):
    def __init__(self, request, status=401):
        auth_status = authkit.AuthenticationStatus(request)
        stage = auth_status.get_pending_stage()
        flows = []
        if request.user.is_authenticated:
            flows.extend(
                [
                    {"id": m["id"]}
                    for m in get_account_adapter().get_reauthentication_methods(
                        request.user
                    )
                ]
            )
        else:
            flows.extend(
                [
                    {
                        "id": "login",
                    },
                    {
                        "id": "signup",
                    },
                ]
            )
            if allauth_app_settings.SOCIALACCOUNT_ENABLED:
                flows.extend(self._provider_flows(request))
        if stage:
            flows.append({"id": stage.key, "is_pending": True})
        data = {"flows": flows}
        if request.user.is_authenticated:
            data["user"] = user_data(request.user)
        meta = {
            "is_authenticated": request.user.is_authenticated,
        }
        add_session_meta(request, meta)
        super().__init__(
            data=data,
            meta=meta,
            status=status,
        )

    def _provider_flows(self, request):
        from allauth.headless.socialaccount.response import provider_flows

        return provider_flows(request)


class AuthenticatedResponse(APIResponse):
    def __init__(self, request, user):
        data = {
            "user": user_data(user),
            "methods": get_authentication_records(request),
        }
        meta = {"is_authenticated": True}
        add_session_meta(request, meta)
        super().__init__(data, meta=meta)


def respond_is_authenticated(request, is_authenticated=None):
    if is_authenticated is None:
        is_authenticated = request.user.is_authenticated
    if is_authenticated:
        return AuthenticatedResponse(request, request.user)
    return UnauthorizedResponse(request)


def user_data(user):
    """Basic user data, also exposed in partly authenticated scenario's
    (e.g. password reset, email verification).
    """
    ret = {
        "id": user.pk,
        "display": user_display(user),
        "has_usable_password": user.has_usable_password(),
    }
    email = EmailAddress.objects.get_primary_email(user)
    if email:
        ret["email"] = email
    username = user_username(user)
    if username:
        ret["username"] = username
    return ret


def add_session_meta(request, meta):
    session_token = sessionkit.expose_session_token(request)
    if session_token:
        meta["session_token"] = session_token
    access_token = authkit.expose_access_token(request)
    if access_token:
        meta["access_token"] = access_token
