from allauth import (
    app_settings as allauth_app_settings,
    app_settings as allauth_settings,
)
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.authentication import get_authentication_records
from allauth.account.models import EmailAddress
from allauth.account.utils import user_display, user_username
from allauth.headless.constants import Flow
from allauth.headless.internal import authkit, sessionkit
from allauth.headless.restkit.response import APIResponse


class BaseAuthenticationResponse(APIResponse):
    def __init__(self, request, user=None, status=None):
        data = {}
        if user and user.is_authenticated:
            data["user"] = user_data(user)
            data["methods"] = (get_authentication_records(request),)
            status = status or 200
        else:
            data["flows"] = self._get_flows(request, user)
            status = 401
        meta = {
            "is_authenticated": user and user.is_authenticated,
        }
        self._add_session_meta(request, meta)
        super().__init__(
            request,
            data=data,
            meta=meta,
            status=status,
        )

    def _add_session_meta(self, request, meta):
        session_token = sessionkit.expose_session_token(request)
        if session_token:
            meta["session_token"] = session_token
        access_token = authkit.expose_access_token(request)
        if access_token:
            meta["access_token"] = access_token

    def _get_flows(self, request, user):
        auth_status = authkit.AuthenticationStatus(request)
        stage = auth_status.get_pending_stage()
        flows = []
        if user and user.is_authenticated:
            flows.extend(
                [
                    {"id": m["id"]}
                    for m in get_account_adapter().get_reauthentication_methods(user)
                ]
            )
        else:
            flows.append(
                {
                    "id": Flow.LOGIN,
                },
            )
            if get_account_adapter().is_open_for_signup(request):
                flows.append(
                    {
                        "id": Flow.SIGNUP,
                    }
                )
            if allauth_app_settings.SOCIALACCOUNT_ENABLED:
                from allauth.headless.socialaccount.response import (
                    provider_flows,
                )

                flows.extend(provider_flows(request))
        if stage:
            flows.append({"id": stage.key, "is_pending": True})
        return flows


class AuthenticationResponse(BaseAuthenticationResponse):
    def __init__(self, request):
        super().__init__(request, user=request.user)


class ReauthenticationResponse(BaseAuthenticationResponse):
    def __init__(self, request):
        super().__init__(request, user=request.user, status=401)


class UnauthorizedResponse(BaseAuthenticationResponse):
    def __init__(self, request):
        super().__init__(request, user=None, status=401)


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


class ConfigResponse(APIResponse):
    def __init__(self, request):
        data = {}
        if allauth_settings.SOCIALACCOUNT_ENABLED:
            from allauth.headless.socialaccount.response import get_config_data

            data.update(get_config_data(request))
        if allauth_settings.MFA_ENABLED:
            from allauth.headless.mfa.response import get_config_data

            data.update(get_config_data(request))
        if allauth_settings.USERSESSIONS_ENABLED:
            from allauth.headless.usersessions.response import get_config_data

            data.update(get_config_data(request))
        return super().__init__(request, data=data)
