from allauth.account.models import Login
from allauth.headless.base.response import APIResponse, AuthenticationResponse
from allauth.headless.base.views import (
    APIView,
    AuthenticatedAPIView,
    AuthenticationStageAPIView,
)
from allauth.headless.mfa import response
from allauth.headless.mfa.inputs import (
    ActivateTOTPInput,
    AddWebAuthnInput,
    AuthenticateInput,
    AuthenticateWebAuthnInput,
    DeleteWebAuthnInput,
    GenerateRecoveryCodesInput,
    LoginWebAuthnInput,
    ReauthenticateWebAuthnInput,
    UpdateWebAuthnInput,
)
from allauth.mfa.adapter import DefaultMFAAdapter, get_adapter
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal import flows as recovery_codes_flows
from allauth.mfa.stages import AuthenticateStage
from allauth.mfa.totp.internal import auth as totp_auth, flows as totp_flows
from allauth.mfa.webauthn.internal import (
    auth as webauthn_auth,
    flows as webauthn_flows,
)


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

    def get(self, request, *args, **kwargs) -> APIResponse:
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


class ManageWebAuthnView(AuthenticatedAPIView):
    input_class = {
        "POST": AddWebAuthnInput,
        "PUT": UpdateWebAuthnInput,
        "DELETE": DeleteWebAuthnInput,
    }

    def get(self, request, *args, **kwargs):
        passwordless = "passwordless" in request.GET
        creation_options = webauthn_flows.begin_registration(
            request, request.user, passwordless
        )
        return response.AddWebAuthnResponse(request, creation_options)

    def get_input_kwargs(self):
        return {"user": self.request.user}

    def post(self, request, *args, **kwargs):
        auth, rc_auth = webauthn_flows.add_authenticator(
            request,
            name=self.input.cleaned_data["name"],
            credential=self.input.cleaned_data["credential"],
        )
        did_generate_recovery_codes = bool(rc_auth)
        return response.AuthenticatorResponse(
            request,
            auth,
            meta={"recovery_codes_generated": did_generate_recovery_codes},
        )

    def put(self, request, *args, **kwargs):
        authenticator = self.input.cleaned_data["id"]
        webauthn_flows.rename_authenticator(
            request, authenticator, self.input.cleaned_data["name"]
        )
        return response.AuthenticatorResponse(request, authenticator)

    def delete(self, request, *args, **kwargs):
        authenticators = self.input.cleaned_data["authenticators"]
        webauthn_flows.remove_authenticators(request, authenticators)
        return response.AuthenticatorsDeletedResponse(request)


class ReauthenticateWebAuthnView(AuthenticatedAPIView):
    input_class = {
        "POST": ReauthenticateWebAuthnInput,
    }

    def get(self, request, *args, **kwargs):
        request_options = webauthn_auth.begin_authentication(request.user)
        return response.WebAuthnRequestOptionsResponse(request, request_options)

    def get_input_kwargs(self):
        return {"user": self.request.user}

    def post(self, request, *args, **kwargs):
        authenticator = self.input.cleaned_data["credential"]
        webauthn_flows.reauthenticate(request, authenticator)
        return AuthenticationResponse(self.request)


class AuthenticateWebAuthnView(AuthenticationStageAPIView):
    input_class = {
        "POST": AuthenticateWebAuthnInput,
    }
    stage_class = AuthenticateStage

    def get(self, request, *args, **kwargs):
        request_options = webauthn_auth.begin_authentication(self.stage.login.user)
        return response.WebAuthnRequestOptionsResponse(request, request_options)

    def get_input_kwargs(self):
        return {"user": self.stage.login.user}

    def post(self, request, *args, **kwargs):
        self.input.save()
        return self.respond_next_stage()


class LoginWebAuthnView(APIView):
    input_class = {
        "POST": LoginWebAuthnInput,
    }

    def get(self, request, *args, **kwargs):
        request_options = webauthn_auth.begin_authentication()
        return response.WebAuthnRequestOptionsResponse(request, request_options)

    def post(self, request, *args, **kwargs):
        authenticator = self.input.cleaned_data["credential"]
        redirect_url = None
        login = Login(user=authenticator.user, redirect_url=redirect_url)
        webauthn_flows.perform_passwordless_login(request, authenticator, login)
        return AuthenticationResponse(request)
