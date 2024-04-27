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
from allauth.mfa import totp
from allauth.mfa.internal import flows
from allauth.mfa.models import Authenticator
from allauth.mfa.stages import AuthenticateStage


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


class ManageTOTPView(AuthenticatedAPIView):
    input_class = {"POST": ActivateTOTPInput}

    def get(self, request, *args, **kwargs):
        authenticator = self._get_authenticator()
        if not authenticator:
            secret = totp.get_totp_secret(regenerate=True)
            return response.TOTPNotFoundResponse(request, secret)
        return response.TOTPResponse(request, authenticator)

    def _get_authenticator(self):
        return Authenticator.objects.filter(
            type=Authenticator.Type.TOTP, user=self.request.user
        ).first()

    def get_input_kwargs(self):
        return {"user": self.request.user}

    def post(self, request, *args, **kwargs):
        authenticator = flows.totp.activate_totp(request, self.input).instance
        return response.TOTPResponse(request, authenticator)

    def delete(self, request, *args, **kwargs):
        authenticator = self._get_authenticator()
        if authenticator:
            authenticator = flows.totp.deactivate_totp(request, authenticator)
        return response.AuthenticatorDeletedResponse(request)


class ManageRecoveryCodesView(AuthenticatedAPIView):
    input_class = GenerateRecoveryCodesInput

    def get(self, request, *args, **kwargs):
        authenticator = flows.recovery_codes.view_recovery_codes(request)
        if not authenticator:
            return response.RecoveryCodesNotFoundResponse(request)
        return response.RecoveryCodesResponse(request, authenticator)

    def post(self, request, *args, **kwargs):
        authenticator = flows.recovery_codes.generate_recovery_codes(request)
        return response.RecoveryCodesResponse(request, authenticator)

    def get_input_kwargs(self):
        return {"user": self.request.user}
