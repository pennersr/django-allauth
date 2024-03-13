from allauth.headless.base.response import APIResponse
from allauth.headless.base.views import (
    AuthenticatedAPIView,
    AuthenticationStageAPIView,
)
from allauth.headless.mfa import response
from allauth.headless.mfa.inputs import ActivateTOTPInput, AuthenticateInput
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


authenticate = AuthenticateView.as_view()


class AuthenticatorsView(AuthenticatedAPIView):
    def get(self, request, *args, **kwargs):
        authenticators = Authenticator.objects.filter(user=request.user)
        return APIResponse(
            data=[{"type": authenticator.type} for authenticator in authenticators]
        )


authenticators = AuthenticatorsView.as_view()


class ManageTOTPView(AuthenticatedAPIView):
    input_class = {"POST": ActivateTOTPInput}

    def get(self, request, *args, **kwargs):
        authenticator = self._get_authenticator()
        if not authenticator:
            return response.respond_totp_inactive(request)
        return response.respond_totp_active(request, authenticator)

    def _get_authenticator(self):
        return Authenticator.objects.filter(
            type=Authenticator.Type.TOTP, user=self.request.user
        ).first()

    def get_input_kwargs(self):
        return {"user": self.request.user}

    def post(self, request, *args, **kwargs):
        authenticator = flows.totp.activate_totp(request, self.input)
        return response.respond_totp_active(request, authenticator)

    def delete(self, request, *args, **kwargs):
        authenticator = self._get_authenticator()
        if authenticator:
            authenticator = flows.totp.deactivate_totp(request, authenticator)
        return APIResponse(status=200)


manage_totp = ManageTOTPView.as_view()
