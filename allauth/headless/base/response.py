from django.http import JsonResponse

from allauth import app_settings as allauth_app_settings
from allauth.account.authentication import get_authentication_records
from allauth.account.models import EmailAddress
from allauth.account.utils import user_display, user_username
from allauth.headless.auth import AuthenticationState


class APIResponse(JsonResponse):
    def __init__(self, data=None, meta=None, status=200):
        d = {"status": status}
        if data is not None:
            d["data"] = data
        if meta is not None:
            d["meta"] = meta
        super().__init__(d, status=status)


class UnauthorizedResponse(APIResponse):
    def __init__(self, request):
        state = AuthenticationState(request)
        stages = state.get_stages()
        flows = [
            {
                "id": "login",
                "url": request.allauth.headless.reverse("headless_login"),
            },
            {
                "id": "signup",
                "url": request.allauth.headless.reverse("headless_signup"),
            },
        ]
        if allauth_app_settings.SOCIALACCOUNT_ENABLED:
            flows.extend(self._provider_flows(request))
        if stages:
            stage = stages[0]
            flows.append(
                {"id": stage.key, "url": stage.get_headless_url(), "is_pending": True}
            )
        super().__init__(
            {"flows": flows},
            meta={
                "is_authenticated": False,
            },
            status=401,
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
        super().__init__(data, meta={"is_authenticated": True})


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
