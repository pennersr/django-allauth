from allauth.account.stages import LoginStage
from allauth.core.internal.httpkit import headed_redirect_response, is_headless_request
from allauth.mfa import app_settings
from allauth.mfa.internal.flows import trust
from allauth.mfa.models import Authenticator
from allauth.mfa.utils import is_mfa_enabled
from allauth.mfa.webauthn.internal.flows import did_use_passwordless_login


class AuthenticateStage(LoginStage):
    # NOTE: Duplicated in `allauth.headless.constants.Flow.MFA_AUTHENTICATE`.
    key = "mfa_authenticate"
    urlname = "mfa_authenticate"

    def handle(self):
        response, cont = None, True
        if self._should_handle(self.request):
            self.state["authentication_required"] = True
            response = headed_redirect_response("mfa_authenticate")
        return response, cont

    def _should_handle(self, request) -> bool:
        if not is_mfa_enabled(
            self.login.user, [Authenticator.Type.TOTP, Authenticator.Type.WEBAUTHN]
        ):
            return False
        if did_use_passwordless_login(request):
            return False
        if trust.is_trusted_browser(request, self.login.user):
            return False
        return True


class TrustStage(LoginStage):
    key = "mfa_trust"
    urlname = "mfa_trust"

    def handle(self):
        auth_stage = self.controller.get_stage(AuthenticateStage.key)
        if (
            not app_settings.TRUST_ENABLED
            or not auth_stage
            or not auth_stage.state.get("authentication_required")
        ):
            return None, True
        client = is_headless_request(self.request)
        if client and client == "app":
            # Trust-this-browser relies on cookies.
            return None, True
        response = headed_redirect_response("mfa_trust")
        return response, True
