from django.core.exceptions import ValidationError

from allauth.account.internal.stagekit import get_pending_stage
from allauth.account.models import Login
from allauth.headless.account.views import SignupView
from allauth.headless.base.response import (
    APIResponse,
    AuthenticationResponse,
    ConflictResponse,
)
from allauth.headless.base.views import (
    APIView,
    AuthenticatedAPIView,
    AuthenticationStageAPIView,
)
from allauth.headless.internal.restkit.response import ErrorResponse
from allauth.headless.mfa import response
from allauth.headless.mfa.inputs import (
    ActivateTOTPInput,
    AddWebAuthnInput,
    AuthenticateInput,
    AuthenticateWebAuthnInput,
    CreateWebAuthnInput,
    DeleteWebAuthnInput,
    GenerateRecoveryCodesInput,
    LoginWebAuthnInput,
    ReauthenticateWebAuthnInput,
    SignupWebAuthnInput,
    TrustInput,
    UpdateWebAuthnInput,
)
from allauth.mfa.adapter import DefaultMFAAdapter, get_adapter
from allauth.mfa.internal.flows import add
from allauth.mfa.internal.flows.trust import trust_browser
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal import flows as recovery_codes_flows
from allauth.mfa.stages import AuthenticateStage, TrustStage
from allauth.mfa.totp.internal import auth as totp_auth, flows as totp_flows
from allauth.mfa.webauthn.internal import (
    auth as webauthn_auth,
    flows as webauthn_flows,
)
from allauth.mfa.webauthn.stages import PasskeySignupStage


def _validate_can_add_authenticator(request):
    try:
        add.validate_can_add_authenticator(request.user)
    except ValidationError as e:
        return ErrorResponse(request, status=409, exception=e)


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
            err = _validate_can_add_authenticator(request)
            if err:
                return err
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

    def handle(self, request, *args, **kwargs):
        if request.method in ["GET", "POST"]:
            err = _validate_can_add_authenticator(request)
            if err:
                return err
        return super().handle(request, *args, **kwargs)

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


class SignupWebAuthnView(SignupView):
    input_class = {
        "POST": SignupWebAuthnInput,
        "PUT": CreateWebAuthnInput,
    }
    by_passkey = True

    def get(self, request, *args, **kwargs):
        resp = self._require_stage()
        if resp:
            return resp
        creation_options = webauthn_flows.begin_registration(
            request, self.stage.login.user, passwordless=True, signup=True
        )
        return response.AddWebAuthnResponse(request, creation_options)

    def _prep_stage(self):
        if hasattr(self, "stage"):
            return self.stage
        self.stage = get_pending_stage(self.request)
        return self.stage

    def _require_stage(self):
        self._prep_stage()
        if not self.stage or self.stage.key != PasskeySignupStage.key:
            return ConflictResponse(self.request)
        return None

    def get_input_kwargs(self):
        ret = super().get_input_kwargs()
        self._prep_stage()
        if self.stage and self.request.method == "PUT":
            ret["user"] = self.stage.login.user
        return ret

    def put(self, request, *args, **kwargs):
        resp = self._require_stage()
        if resp:
            return resp
        webauthn_flows.signup_authenticator(
            request,
            user=self.stage.login.user,
            name=self.input.cleaned_data["name"],
            credential=self.input.cleaned_data["credential"],
        )
        self.stage.exit()
        return AuthenticationResponse(request)


class TrustView(AuthenticationStageAPIView):
    input_class = TrustInput
    stage_class = TrustStage

    def post(self, request, *args, **kwargs):
        trust = self.input.cleaned_data["trust"]
        response = self.respond_next_stage()
        if trust:
            trust_browser(request, self.stage.login.user, response)
        return response
