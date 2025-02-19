from http import HTTPStatus

from allauth import app_settings as allauth_settings
from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.app_settings import LoginMethod
from allauth.account.authentication import get_authentication_records
from allauth.account.internal import flows
from allauth.account.internal.stagekit import LOGIN_SESSION_KEY
from allauth.headless.adapter import get_adapter
from allauth.headless.constants import Flow
from allauth.headless.internal import authkit
from allauth.headless.internal.restkit.response import APIResponse
from allauth.mfa import app_settings as mfa_settings


class BaseAuthenticationResponse(APIResponse):
    def __init__(self, request, user=None, status=None):
        data = {}
        if user and user.is_authenticated:
            adapter = get_adapter()
            data["user"] = adapter.serialize_user(user)
            data["methods"] = get_authentication_records(request)
            status = status or HTTPStatus.OK
        else:
            status = status or HTTPStatus.UNAUTHORIZED
        if status != HTTPStatus.OK:
            data["flows"] = self._get_flows(request, user)
        meta = {
            "is_authenticated": user and user.is_authenticated,
        }
        super().__init__(
            request,
            data=data,
            meta=meta,
            status=status,
        )

    def _get_flows(self, request, user):
        auth_status = authkit.AuthenticationStatus(request)
        ret = []
        if user and user.is_authenticated:
            ret.extend(flows.reauthentication.get_reauthentication_flows(user))
        else:
            if not allauth_settings.SOCIALACCOUNT_ONLY:
                ret.append({"id": Flow.LOGIN})
            if account_settings.LOGIN_BY_CODE_ENABLED:
                ret.append({"id": Flow.LOGIN_BY_CODE})
            if (
                get_account_adapter().is_open_for_signup(request)
                and not allauth_settings.SOCIALACCOUNT_ONLY
            ):
                ret.append({"id": Flow.SIGNUP})
            if allauth_settings.SOCIALACCOUNT_ENABLED:
                from allauth.headless.socialaccount.response import (
                    provider_flows,
                )

                ret.extend(provider_flows(request))
            if allauth_settings.MFA_ENABLED:
                if mfa_settings.PASSKEY_LOGIN_ENABLED:
                    ret.append({"id": Flow.MFA_LOGIN_WEBAUTHN})
        stage_key = None
        stage = auth_status.get_pending_stage()
        if stage:
            stage_key = stage.key
        else:
            lsk = request.session.get(LOGIN_SESSION_KEY)
            if isinstance(lsk, str):
                stage_key = lsk
        if stage_key:
            pending_flow = {"id": stage_key, "is_pending": True}
            if stage and stage_key == Flow.MFA_AUTHENTICATE:
                self._enrich_mfa_flow(stage, pending_flow)
            self._upsert_pending_flow(ret, pending_flow)

        if (
            not allauth_settings.SOCIALACCOUNT_ONLY
            and account_settings.PASSWORD_RESET_BY_CODE_ENABLED
        ):
            from allauth.account.internal.flows import password_reset_by_code

            ret.append(
                {
                    "id": Flow.PASSWORD_RESET_BY_CODE,
                    "is_pending": bool(
                        password_reset_by_code.PasswordResetVerificationProcess.resume(
                            request
                        )
                    ),
                }
            )
        return ret

    def _upsert_pending_flow(self, flows, pending_flow):
        flow = next((flow for flow in flows if flow["id"] == pending_flow["id"]), None)
        if flow:
            flow.update(pending_flow)
        else:
            flows.append(pending_flow)

    def _enrich_mfa_flow(self, stage, flow: dict) -> None:
        from allauth.mfa.adapter import get_adapter as get_mfa_adapter
        from allauth.mfa.models import Authenticator

        adapter = get_mfa_adapter()
        types = []
        for typ in Authenticator.Type:
            if adapter.is_mfa_enabled(stage.login.user, types=[typ]):
                types.append(typ)
        flow["types"] = types


class AuthenticationResponse(BaseAuthenticationResponse):
    def __init__(self, request):
        super().__init__(request, user=request.user)

    @classmethod
    def from_response(cls, request, response):
        """
        The response might be a headed redirect to e.g. the confirmation
        email page, because allauth.account is not (much) headless
        aware. Also, what if an adapter method return headed responses in
        post_login()?  So, let's ensure we always return a headless
        response.
        """
        if isinstance(response, AuthenticationResponse):
            return response
        return AuthenticationResponse(request)


class ReauthenticationResponse(BaseAuthenticationResponse):
    def __init__(self, request):
        super().__init__(request, user=request.user, status=HTTPStatus.UNAUTHORIZED)


class UnauthorizedResponse(BaseAuthenticationResponse):
    def __init__(self, request, status=HTTPStatus.UNAUTHORIZED):
        super().__init__(request, user=None, status=status)


class ForbiddenResponse(APIResponse):
    def __init__(self, request):
        super().__init__(request, status=HTTPStatus.FORBIDDEN)


class ConflictResponse(APIResponse):
    def __init__(self, request):
        super().__init__(request, status=HTTPStatus.CONFLICT)


def get_config_data(request):
    login_methods = account_settings.LOGIN_METHODS
    data = {
        "login_methods": list(login_methods),
        "is_open_for_signup": get_account_adapter().is_open_for_signup(request),
        "email_verification_by_code_enabled": account_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED,
        "login_by_code_enabled": account_settings.LOGIN_BY_CODE_ENABLED,
        "password_reset_by_code_enabled": account_settings.PASSWORD_RESET_BY_CODE_ENABLED,
    }
    # NOTE: For backwards compatibility only.
    if LoginMethod.EMAIL in login_methods and LoginMethod.USERNAME in login_methods:
        data["authentication_method"] = "username_email"
    elif LoginMethod.EMAIL in login_methods:
        data["authentication_method"] = "email"
    elif LoginMethod.USERNAME in login_methods:
        data["authentication_method"] = "username"
    # (end NOTE)
    return {"account": data}


class ConfigResponse(APIResponse):
    def __init__(self, request):
        data = get_config_data(request)
        if allauth_settings.SOCIALACCOUNT_ENABLED:
            from allauth.headless.socialaccount.response import (
                get_config_data as get_socialaccount_config_data,
            )

            data.update(get_socialaccount_config_data(request))
        if allauth_settings.MFA_ENABLED:
            from allauth.headless.mfa.response import (
                get_config_data as get_mfa_config_data,
            )

            data.update(get_mfa_config_data(request))
        if allauth_settings.USERSESSIONS_ENABLED:
            from allauth.headless.usersessions.response import (
                get_config_data as get_usersessions_config_data,
            )

            data.update(get_usersessions_config_data(request))
        return super().__init__(request, data=data)


class RateLimitResponse(APIResponse):
    def __init__(self, request):
        super().__init__(request, status=HTTPStatus.TOO_MANY_REQUESTS)
