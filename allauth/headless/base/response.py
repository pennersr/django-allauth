from allauth import app_settings as allauth_settings
from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.authentication import get_authentication_records
from allauth.account.internal import flows
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
            status = status or 200
        else:
            status = status or 401
        if status != 200:
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
                code_flow = {"id": Flow.LOGIN_BY_CODE}
                _, data = flows.login_by_code.get_pending_login(request, peek=True)
                if data:
                    code_flow["is_pending"] = True
                ret.append(code_flow)
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
            lsk = request.session.get(flows.login.LOGIN_SESSION_KEY)
            if isinstance(lsk, str):
                stage_key = lsk
        if stage_key:
            pending_flow = {"id": stage_key, "is_pending": True}
            if stage and stage_key == Flow.MFA_AUTHENTICATE:
                self._enrich_mfa_flow(stage, pending_flow)
            ret.append(pending_flow)
        return ret

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


class ReauthenticationResponse(BaseAuthenticationResponse):
    def __init__(self, request):
        super().__init__(request, user=request.user, status=401)


class UnauthorizedResponse(BaseAuthenticationResponse):
    def __init__(self, request, status=401):
        super().__init__(request, user=None, status=status)


class ForbiddenResponse(APIResponse):
    def __init__(self, request):
        super().__init__(request, status=403)


class ConflictResponse(APIResponse):
    def __init__(self, request):
        super().__init__(request, status=409)


def get_config_data(request):
    data = {
        "authentication_method": account_settings.AUTHENTICATION_METHOD,
        "is_open_for_signup": get_account_adapter().is_open_for_signup(request),
    }
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
        super().__init__(request, status=429)
