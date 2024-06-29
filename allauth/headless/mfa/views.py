from allauth.headless.base.response import AuthenticationResponse
from allauth.headless.base.views import (
    AuthenticatedAPIView,
    AuthenticationStageAPIView,
)
from allauth.headless.mfa import response
from allauth.headless.mfa.inputs import (
    ActivateTOTPInput,
    AuthenticateInput,
    GenerateRecoveryCodesInput,
)
from allauth.mfa.adapter import DefaultMFAAdapter, get_adapter
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal import flows as recovery_codes_flows
from allauth.mfa.stages import AuthenticateStage
from allauth.mfa.totp.internal import auth as totp_auth, flows as totp_flows


class AuthenticateView(AuthenticationStageAPIView):
    input_class = AuthenticateInput
    stage_class = AuthenticateStage

    def post(self, request, *args, **kwargs):
        self.input.save()
        return self.respond_next_stage()

    def get_input_kwargs(self):
        return {"user": self.stage.login.user}


class ReauthenticateView(AuthenticatedAPIView):
    input_class = AuthenticateInput

    def post(self, request, *args, **kwargs):
        self.input.save()
        return AuthenticationResponse(self.request)

    def get_input_kwargs(self):
        return {"user": self.request.user}


class AuthenticatorsView(AuthenticatedAPIView):
    def get(self, request, *args, **kwargs):
        authenticators = Authenticator.objects.filter(user=request.user)
        return response.AuthenticatorsResponse(request, authenticators)


# TODO: Enforce reauthentication
class ManageTOTPView(AuthenticatedAPIView):
    input_class = {"POST": ActivateTOTPInput}

    def get(self, request, *args, **kwargs):
        authenticator = self._get_authenticator()
        if not authenticator:
            adapter: DefaultMFAAdapter = get_adapter()
            secret = totp_auth.get_totp_secret(regenerate=True)
            totp_url: str = adapter.build_totp_url(request.user, secret)
            return response.TOTPNotFoundResponse(request, secret, totp_url)
        return response.TOTPResponse(request, authenticator)

    def _get_authenticator(self):
        return Authenticator.objects.filter(
            type=Authenticator.Type.TOTP, user=self.request.user
        ).first()

    def get_input_kwargs(self):
        return {"user": self.request.user}

    def post(self, request, *args, **kwargs):
        authenticator = totp_flows.activate_totp(request, self.input)[0]
        return response.TOTPResponse(request, authenticator)

    def delete(self, request, *args, **kwargs):
        authenticator = self._get_authenticator()
        if authenticator:
            authenticator = totp_flows.deactivate_totp(request, authenticator)
        return response.AuthenticatorDeletedResponse(request)


class ManageRecoveryCodesView(AuthenticatedAPIView):
    input_class = GenerateRecoveryCodesInput

    def get(self, request, *args, **kwargs):
        authenticator = recovery_codes_flows.view_recovery_codes(request)
        if not authenticator:
            return response.RecoveryCodesNotFoundResponse(request)
        return response.RecoveryCodesResponse(request, authenticator)

    def post(self, request, *args, **kwargs):
        authenticator = recovery_codes_flows.generate_recovery_codes(request)
        return response.RecoveryCodesResponse(request, authenticator)

    def get_input_kwargs(self):
        return {"user": self.request.user}
