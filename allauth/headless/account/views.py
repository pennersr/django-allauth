from django.utils.decorators import method_decorator

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal import flows
from allauth.account.internal.flows import password_change, password_reset
from allauth.account.models import EmailAddress
from allauth.account.stages import EmailVerificationStage, LoginStageController
from allauth.account.utils import send_email_confirmation
from allauth.core import ratelimit
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.decorators import rate_limit
from allauth.headless.account import response
from allauth.headless.account.inputs import (
    AddEmailInput,
    ChangePasswordInput,
    ConfirmLoginCodeInput,
    DeleteEmailInput,
    LoginInput,
    MarkAsPrimaryEmailInput,
    ReauthenticateInput,
    RequestLoginCodeInput,
    RequestPasswordResetInput,
    ResetPasswordInput,
    ResetPasswordKeyInput,
    SelectEmailInput,
    SignupInput,
    VerifyEmailInput,
)
from allauth.headless.base.response import (
    APIResponse,
    AuthenticationResponse,
    ConflictResponse,
    ForbiddenResponse,
)
from allauth.headless.base.views import APIView, AuthenticatedAPIView
from allauth.headless.internal import authkit
from allauth.headless.internal.restkit.response import ErrorResponse


class RequestLoginCodeView(APIView):
    input_class = RequestLoginCodeInput

    def post(self, request, *args, **kwargs):
        flows.login_by_code.request_login_code(
            self.request, self.input.cleaned_data["email"]
        )
        return AuthenticationResponse(self.request)


class ConfirmLoginCodeView(APIView):
    input_class = ConfirmLoginCodeInput

    def dispatch(self, request, *args, **kwargs):
        auth_status = authkit.AuthenticationStatus(request)
        self.stage = auth_status.get_pending_stage()
        if not self.stage:
            return ConflictResponse(request)
        self.user, self.pending_login = flows.login_by_code.get_pending_login(
            request, self.stage.login, peek=True
        )
        if not self.pending_login:
            return ConflictResponse(request)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        flows.login_by_code.perform_login_by_code(self.request, self.stage, None)
        return AuthenticationResponse(request)

    def get_input_kwargs(self):
        kwargs = super().get_input_kwargs()
        kwargs["code"] = (
            self.pending_login.get("code", "") if self.pending_login else ""
        )
        return kwargs

    def handle_invalid_input(self, input):
        flows.login_by_code.record_invalid_attempt(self.request, self.stage.login)
        return super().handle_invalid_input(input)


@method_decorator(rate_limit(action="login"), name="handle")
class LoginView(APIView):
    input_class = LoginInput

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return ConflictResponse(request)
        credentials = self.input.cleaned_data
        flows.login.perform_password_login(request, credentials, self.input.login)
        return AuthenticationResponse(self.request)


@method_decorator(rate_limit(action="signup"), name="handle")
class SignupView(APIView):
    input_class = {"POST": SignupInput}
    by_passkey = False

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return ConflictResponse(request)
        if not get_account_adapter().is_open_for_signup(request):
            return ForbiddenResponse(request)
        user, resp = self.input.try_save(request)
        if not resp:
            try:
                flows.signup.complete_signup(
                    request, user=user, by_passkey=self.by_passkey
                )
            except ImmediateHttpResponse:
                pass
        return AuthenticationResponse(request)


class SessionView(APIView):
    def get(self, request, *args, **kwargs):
        return AuthenticationResponse(request)

    def delete(self, request, *args, **kwargs):
        adapter = get_account_adapter()
        adapter.logout(request)
        return AuthenticationResponse(request)


class VerifyEmailView(APIView):
    input_class = VerifyEmailInput

    def handle(self, request, *args, **kwargs):
        self.stage = LoginStageController.enter(request, EmailVerificationStage.key)
        return super().handle(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        key = request.headers.get("x-email-verification-key", "")
        input = self.input_class({"key": key})
        if not input.is_valid():
            return ErrorResponse(request, input=input)
        verification = input.cleaned_data["key"]
        return response.VerifyEmailResponse(request, verification, stage=self.stage)

    def post(self, request, *args, **kwargs):
        confirmation = self.input.cleaned_data["key"]
        email_address = confirmation.confirm(request)
        if not email_address:
            # Should not happen, VerifyInputInput should have verified all
            # preconditions.
            return APIResponse(status=500)
        if self.stage:
            # Verifying email as part of login/signup flow, so emit a
            # authentication status response.
            self.stage.exit()
        return AuthenticationResponse(self.request)


class RequestPasswordResetView(APIView):
    input_class = RequestPasswordResetInput

    def post(self, request, *args, **kwargs):
        r429 = ratelimit.consume_or_429(
            self.request,
            action="reset_password",
            key=self.input.cleaned_data["email"].lower(),
        )
        if r429:
            return r429
        self.input.save(request)
        return response.RequestPasswordResponse(request)


@method_decorator(rate_limit(action="reset_password_from_key"), name="handle")
class ResetPasswordView(APIView):
    input_class = ResetPasswordInput

    def get(self, request, *args, **kwargs):
        key = request.headers.get("X-Password-Reset-Key", "")
        input = ResetPasswordKeyInput({"key": key})
        if not input.is_valid():
            return ErrorResponse(request, input=input)
        return response.PasswordResetKeyResponse(request, input.user)

    def post(self, request, *args, **kwargs):
        flows.password_reset.reset_password(
            self.input.user, self.input.cleaned_data["password"]
        )
        password_reset.finalize_password_reset(request, self.input.user)
        return AuthenticationResponse(self.request)


@method_decorator(rate_limit(action="change_password"), name="handle")
class ChangePasswordView(AuthenticatedAPIView):
    input_class = ChangePasswordInput

    def post(self, request, *args, **kwargs):
        password_change.change_password(
            self.request.user, self.input.cleaned_data["new_password"]
        )
        is_set = not self.input.cleaned_data.get("current_password")
        if is_set:
            password_change.finalize_password_set(request, request.user)
        else:
            password_change.finalize_password_change(request, request.user)
        return AuthenticationResponse(request)

    def get_input_kwargs(self):
        return {"user": self.request.user}


@method_decorator(rate_limit(action="manage_email"), name="handle")
class ManageEmailView(AuthenticatedAPIView):
    input_class = {
        "POST": AddEmailInput,
        "PUT": SelectEmailInput,
        "DELETE": DeleteEmailInput,
        "PATCH": MarkAsPrimaryEmailInput,
    }

    def get(self, request, *args, **kwargs):
        return self._respond_email_list()

    def _respond_email_list(self):
        addrs = EmailAddress.objects.filter(user=self.request.user)
        return response.EmailAddressesResponse(self.request, addrs)

    def post(self, request, *args, **kwargs):
        flows.manage_email.add_email(request, self.input)
        return self._respond_email_list()

    def delete(self, request, *args, **kwargs):
        addr = self.input.cleaned_data["email"]
        flows.manage_email.delete_email(request, addr)
        return self._respond_email_list()

    def patch(self, request, *args, **kwargs):
        addr = self.input.cleaned_data["email"]
        flows.manage_email.mark_as_primary(request, addr)
        return self._respond_email_list()

    def put(self, request, *args, **kwargs):
        addr = self.input.cleaned_data["email"]
        sent = send_email_confirmation(request, request.user, email=addr.email)
        return response.RequestEmailVerificationResponse(
            request, verification_sent=sent
        )

    def get_input_kwargs(self):
        return {"user": self.request.user}


@method_decorator(rate_limit(action="reauthenticate"), name="handle")
class ReauthenticateView(AuthenticatedAPIView):
    input_class = ReauthenticateInput

    def post(self, request, *args, **kwargs):
        flows.reauthentication.reauthenticate_by_password(self.request)
        return AuthenticationResponse(self.request)

    def get_input_kwargs(self):
        return {"user": self.request.user}
