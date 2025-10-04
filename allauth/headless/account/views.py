from http import HTTPStatus

from django.utils.decorators import method_decorator

from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal import flows
from allauth.account.internal.flows import (
    email_verification,
    manage_email,
    password_change,
    password_reset,
    password_reset_by_code,
)
from allauth.account.internal.flows.email_verification import (
    send_verification_email_to_address,
)
from allauth.account.internal.flows.email_verification_by_code import (
    EmailVerificationProcess,
)
from allauth.account.internal.flows.phone_verification import (
    PhoneVerificationStageProcess,
)
from allauth.account.stages import (
    EmailVerificationStage,
    LoginStageController,
    PhoneVerificationStage,
)
from allauth.core import ratelimit
from allauth.core.exceptions import ImmediateHttpResponse, RateLimited
from allauth.decorators import rate_limit
from allauth.headless.account import response
from allauth.headless.account.inputs import (
    AddEmailInput,
    ChangeEmailInput,
    ChangePasswordInput,
    ChangePhoneInput,
    ConfirmLoginCodeInput,
    DeleteEmailInput,
    LoginInput,
    MarkAsPrimaryEmailInput,
    ReauthenticateInput,
    RequestLoginCodeInput,
    RequestPasswordResetInput,
    ResendEmailVerificationInput,
    ResetPasswordInput,
    ResetPasswordKeyInput,
    SignupInput,
    VerifyEmailInput,
    VerifyPhoneInput,
)
from allauth.headless.base.response import (
    APIResponse,
    AuthenticationResponse,
    ConflictResponse,
    ForbiddenResponse,
    RateLimitResponse,
)
from allauth.headless.base.views import APIView, AuthenticatedAPIView
from allauth.headless.internal import authkit
from allauth.headless.internal.restkit.response import ErrorResponse


class RequestLoginCodeView(APIView):
    input_class = RequestLoginCodeInput

    def post(self, request, *args, **kwargs):
        flows.login_by_code.LoginCodeVerificationProcess.initiate(
            request=self.request,
            user=self.input._user,
            email=self.input.cleaned_data.get("email"),
            phone=self.input.cleaned_data.get("phone"),
        )
        return AuthenticationResponse(self.request)


class ConfirmLoginCodeView(APIView):
    input_class = ConfirmLoginCodeInput

    def dispatch(self, request, *args, **kwargs):
        auth_status = authkit.AuthenticationStatus(request)
        self.stage = auth_status.get_pending_stage()
        if not self.stage:
            return ConflictResponse(request)
        self.process = flows.login_by_code.LoginCodeVerificationProcess.resume(
            self.stage
        )
        if not self.process:
            return ConflictResponse(request)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = self.process.finish(None)
        return AuthenticationResponse.from_response(request, response)

    def get_input_kwargs(self):
        kwargs = super().get_input_kwargs()
        kwargs["code"] = self.process.code
        return kwargs

    def handle_invalid_input(self, input):
        self.process.record_invalid_attempt()
        return super().handle_invalid_input(input)


@method_decorator(rate_limit(action="login"), name="handle")
class LoginView(APIView):
    input_class = LoginInput

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return ConflictResponse(request)
        credentials = self.input.cleaned_data
        response = flows.login.perform_password_login(
            request, credentials, self.input.login
        )
        return AuthenticationResponse.from_response(request, response)


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
                resp = flows.signup.complete_signup(
                    request, user=user, by_passkey=self.by_passkey
                )
            except ImmediateHttpResponse:
                pass
        return AuthenticationResponse.from_response(request, resp)


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
        if (
            not self.stage
            and account_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED
            and not request.user.is_authenticated
        ):
            return ConflictResponse(request)
        self.process = None
        if account_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
            self.process = (
                flows.email_verification_by_code.EmailVerificationProcess.resume(
                    request
                )
            )
            if not self.process:
                return ConflictResponse(request)
        return super().handle(request, *args, **kwargs)

    def get_input_kwargs(self):
        return {"process": self.process}

    def handle_invalid_input(self, input: VerifyEmailInput):
        if self.process:
            self.process.record_invalid_attempt()
        return super().handle_invalid_input(input)

    def get(self, request, *args, **kwargs):
        key = request.headers.get("x-email-verification-key", "")
        input = self.input_class({"key": key}, process=self.process)
        if not input.is_valid():
            if self.process:
                self.process.record_invalid_attempt()
            return ErrorResponse(request, input=input)
        if self.process:
            email_address = self.process.email_address
        else:
            email_address = input.verification.email_address
        return response.VerifyEmailResponse(request, email_address, stage=self.stage)

    def post(self, request, *args, **kwargs):
        if self.process:
            email_address = self.process.finish()
        else:
            email_address = self.input.verification.confirm(request)
        if not email_address:
            # Should not happen, VerifyInputInput should have verified all
            # preconditions.
            return APIResponse(request, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        response = None
        if self.stage:
            # Verifying email as part of login/signup flow may imply the user is
            # to be logged in...
            response = email_verification.login_on_verification(request, email_address)
        return AuthenticationResponse.from_response(request, response)


class VerifyPhoneView(APIView):
    input_class = VerifyPhoneInput

    def handle(self, request, *args, **kwargs):
        self.stage = LoginStageController.enter(request, PhoneVerificationStage.key)
        if self.stage:
            self.process = (
                flows.phone_verification.PhoneVerificationStageProcess.resume(
                    self.stage
                )
            )
        else:
            if not request.user.is_authenticated:
                return ConflictResponse(request)
            self.process = (
                flows.phone_verification.ChangePhoneVerificationProcess.resume(request)
            )
        if not self.process:
            return ConflictResponse(request)
        return super().handle(request, *args, **kwargs)

    def get_input_kwargs(self):
        return {
            "code": self.process.code,
            "user": self.process.user,
            "phone": self.process.phone,
        }

    def handle_invalid_input(self, input: VerifyPhoneInput):
        self.process.record_invalid_attempt()
        return super().handle_invalid_input(input)

    def post(self, request, *args, **kwargs):
        self.process.finish()
        response = None
        if self.stage:
            response = self.stage.exit()
        return AuthenticationResponse.from_response(request, response)


class ResendPhoneVerificationCodeView(APIView):
    handle_json_input = False

    def post(self, request, *args, **kwargs):
        process = None
        stage = LoginStageController.enter(request, PhoneVerificationStage.key)
        if stage:
            process = flows.phone_verification.PhoneVerificationStageProcess.resume(
                stage
            )
        if not process or not process.can_resend:
            return ConflictResponse(request)
        try:
            process.resend()
        except RateLimited:
            return RateLimitResponse(request)
        return APIResponse(request)


class ResendEmailVerificationCodeView(APIView):
    handle_json_input = False

    def post(self, request, *args, **kwargs):
        if not account_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
            return ConflictResponse(request)
        process = flows.email_verification_by_code.EmailVerificationProcess.resume(
            request
        )
        if not process or not process.can_resend:
            return ConflictResponse(request)
        try:
            process.resend()
        except RateLimited:
            return RateLimitResponse(request)
        return APIResponse(request)


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
        if account_settings.PASSWORD_RESET_BY_CODE_ENABLED:
            return AuthenticationResponse(request)
        return response.RequestPasswordResponse(request)


@method_decorator(rate_limit(action="reset_password_from_key"), name="handle")
class ResetPasswordView(APIView):
    input_class = ResetPasswordInput

    def handle_invalid_input(self, input: ResetPasswordInput):
        if self.process and "key" in input.errors:
            self.process.record_invalid_attempt()
        return super().handle_invalid_input(input)

    def handle(self, request, *args, **kwargs):
        self.process = None
        if account_settings.PASSWORD_RESET_BY_CODE_ENABLED:
            self.process = (
                password_reset_by_code.PasswordResetVerificationProcess.resume(
                    self.request
                )
            )
            if not self.process:
                return ConflictResponse(request)
        return super().handle(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        key = request.headers.get("X-Password-Reset-Key", "")
        if self.process:
            input = ResetPasswordKeyInput({"key": key}, code=self.process.code)
            if not input.is_valid():
                self.process.record_invalid_attempt()
                return ErrorResponse(request, input=input)
            self.process.confirm_code()
            return response.PasswordResetKeyResponse(request, self.process.user)
        else:
            input = ResetPasswordKeyInput({"key": key})
            if not input.is_valid():
                return ErrorResponse(request, input=input)
            return response.PasswordResetKeyResponse(request, input.user)

    def get_input_kwargs(self):
        ret = {}
        if self.process:
            ret.update({"code": self.process.code, "user": self.process.user})
        return ret

    def post(self, request, *args, **kwargs):
        user = self.input.user
        flows.password_reset.reset_password(user, self.input.cleaned_data["password"])
        if self.process:
            self.process.confirm_code()
            self.process.finish()
        else:
            password_reset.finalize_password_reset(request, user)
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


class ManageEmailView(APIView):
    input_class = {
        "POST": AddEmailInput,
        "PUT": ResendEmailVerificationInput,
        "DELETE": DeleteEmailInput,
        "PATCH": MarkAsPrimaryEmailInput,
    }

    def dispatch(self, request, *args, **kwargs):
        self.verification_stage_process = None
        if request.user.is_authenticated:
            self.user = request.user
        elif request.method != "POST":
            return AuthenticationResponse(request)
        else:
            self.verification_stage_process = EmailVerificationProcess.resume(request)
            if (
                not self.verification_stage_process
                or not self.verification_stage_process.can_change
            ):
                return ConflictResponse(request)
            self.user = self.verification_stage_process.user
        resp = ratelimit.consume_or_429(request, action="manage_email", user=self.user)
        if resp:
            return resp
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self._respond_email_list()

    def _respond_email_list(self):
        addrs = manage_email.list_email_addresses(self.request, self.user)
        return response.EmailAddressesResponse(self.request, addrs)

    def post(self, request, *args, **kwargs):
        if self.verification_stage_process:
            self.verification_stage_process.change_to(
                email=self.input.cleaned_data["email"],
                account_already_exists=self.input.account_already_exists,
            )
        else:
            flows.manage_email.add_email(request, self.input)
        return self._respond_email_list()

    def delete(self, request, *args, **kwargs):
        addr = self.input.cleaned_data["email"]
        if addr.pk:
            flows.manage_email.delete_email(request, addr)
        else:
            self.input.process.abort()
        return self._respond_email_list()

    def patch(self, request, *args, **kwargs):
        addr = self.input.cleaned_data["email"]
        flows.manage_email.mark_as_primary(request, addr)
        return self._respond_email_list()

    def put(self, request, *args, **kwargs):
        addr = self.input.cleaned_data["email"]
        if process := self.input.process:
            sent = False
            if process.can_resend:
                try:
                    self.input.process.resend()
                    sent = True
                except RateLimited:
                    pass
        else:
            sent = send_verification_email_to_address(request, addr)
        return response.RequestEmailVerificationResponse(
            request, verification_sent=sent
        )

    def get_input_class(self):
        if self.verification_stage_process:
            return ChangeEmailInput
        return super().get_input_class()

    def get_input_kwargs(self):
        if self.verification_stage_process:
            return {"email": self.verification_stage_process.email}
        return {"user": self.user}


class ManagePhoneView(APIView):
    input_class = ChangePhoneInput

    def dispatch(self, request, *args, **kwargs):
        self.verification_stage_process = None
        if request.user.is_authenticated:
            self.user = request.user
        elif request.method == "GET":
            return AuthenticationResponse(request)
        elif request.method == "POST":
            stage = LoginStageController.enter(request, PhoneVerificationStage.key)
            if stage:
                self.verification_stage_process = PhoneVerificationStageProcess.resume(
                    stage
                )
            if (
                not self.verification_stage_process
                or not self.verification_stage_process.can_change
            ):
                return ConflictResponse(request)
            self.user = self.verification_stage_process.user
        resp = ratelimit.consume_or_429(request, action="change_phone", user=self.user)
        if resp:
            return resp
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        phone_numbers = []
        phone_verified = get_account_adapter().get_phone(self.request.user)
        if phone_verified:
            phone_numbers.append(
                {"phone": phone_verified[0], "verified": phone_verified[1]}
            )
        return response.PhoneNumbersResponse(self.request, phone_numbers)

    def post(self, request, *args, **kwargs):
        phone = self.input.cleaned_data["phone"]
        if self.verification_stage_process:
            self.verification_stage_process.change_to(
                phone=phone, account_already_exists=self.input.account_already_exists
            )
        else:
            flows.phone_verification.ChangePhoneVerificationProcess.initiate(
                self.request,
                phone,
            )
        return response.PhoneNumbersResponse(
            self.request,
            [
                {
                    "phone": phone,
                    "verified": False,
                }
            ],
            status=HTTPStatus.ACCEPTED,
        )

    def get_input_kwargs(self):
        phone = None
        phone_verified = get_account_adapter().get_phone(self.user)
        if phone_verified:
            phone = phone_verified[0]
        return {"phone": phone, "user": self.user}


@method_decorator(rate_limit(action="reauthenticate"), name="handle")
class ReauthenticateView(AuthenticatedAPIView):
    input_class = ReauthenticateInput

    def post(self, request, *args, **kwargs):
        flows.reauthentication.reauthenticate_by_password(self.request)
        return AuthenticationResponse(self.request)

    def get_input_kwargs(self):
        return {"user": self.request.user}
