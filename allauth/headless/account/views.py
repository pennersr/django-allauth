from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal import flows
from allauth.account.internal.flows import password_change, password_reset
from allauth.account.models import EmailAddress, Login
from allauth.account.stages import EmailVerificationStage, LoginStageController
from allauth.account.utils import complete_signup, send_email_confirmation
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.headless.account.inputs import (
    AddEmailInput,
    ChangePasswordInput,
    DeleteEmailInput,
    LoginInput,
    MarkAsPrimaryEmailInput,
    ReauthenticateInput,
    RequestPasswordResetInput,
    ResetPasswordInput,
    ResetPasswordKeyInput,
    SelectEmailInput,
    SignupInput,
    VerifyEmailInput,
)
from allauth.headless.base import response
from allauth.headless.base.views import APIView, AuthenticatedAPIView


class LoginView(APIView):
    input_class = LoginInput

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return response.UnauthorizedResponse(self.request)
        return response.AuthenticatedResponse(self.request, self.request.user)

    def post(self, request, *args, **kwargs):
        credentials = self.input.cleaned_data
        user = get_account_adapter().authenticate(self.request, **credentials)
        if user:
            login = Login(user=user, email=credentials.get("email"))
            flows.login.perform_password_login(request, credentials, login)
        return response.respond_is_authenticated(self.request)


login = LoginView.as_view()


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        adapter = get_account_adapter()
        adapter.logout(request)
        return response.respond_is_authenticated(request)


logout = LogoutView.as_view()


class SignupView(APIView):
    input_class = SignupInput

    def post(self, request, *args, **kwargs):
        user, resp = self.input.try_save(request)
        if not resp:
            try:
                complete_signup(
                    request,
                    user,
                    email_verification=None,
                    success_url=None,
                )
            except ImmediateHttpResponse:
                pass
        return response.respond_is_authenticated(request)


signup = SignupView.as_view()


class AuthView(AuthenticatedAPIView):
    def get(self, request, *args, **kwargs):
        return response.AuthenticatedResponse(request, self.request.user)


auth = AuthView.as_view()


class VerifyEmailView(APIView):
    input_class = VerifyEmailInput

    def handle(self, request, *args, **kwargs):
        self.stage = LoginStageController.enter(request, EmailVerificationStage.key)
        return super().handle(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        input = self.input_class(request.GET)
        if not input.is_valid():
            return input.respond_error()
        verification = input.cleaned_data["key"]
        data = {
            "email": verification.email_address.email,
            "user": response.user_data(verification.email_address.user),
            "is_authenticating": self.stage is not None,
        }
        return response.APIResponse(data)

    def post(self, request, *args, **kwargs):
        confirmation = self.input.cleaned_data["key"]
        email_address = confirmation.confirm(request)
        if self.stage:
            # Verifying email as part of login/signup flow, so emit a
            # authentication status response.
            if not email_address:
                return response.UnauthorizedResponse(self.request)
            self.stage.exit()
            return response.respond_is_authenticated(self.request)
        else:
            return response.APIResponse(status=200 if email_address else 400)


verify_email = VerifyEmailView.as_view()


class RequestPasswordResetView(APIView):
    input_class = RequestPasswordResetInput

    def post(self, request, *args, **kwargs):
        self.input.save(request)
        data = {}
        return response.APIResponse(data)


request_password_reset = RequestPasswordResetView.as_view()


class ResetPasswordView(APIView):
    input_class = ResetPasswordInput

    def get(self, request, *args, **kwargs):
        input = ResetPasswordKeyInput(request.GET)
        if not input.is_valid():
            return input.respond_error()
        data = {"user": response.user_data(input.user)}
        return response.APIResponse(data)

    def post(self, request, *args, **kwargs):
        flows.password_reset.reset_password(
            self.input.user, self.input.cleaned_data["password"]
        )
        password_reset.finalize_password_reset(request, self.input.user)
        return response.APIResponse()


reset_password = ResetPasswordView.as_view()


class ChangePasswordView(AuthenticatedAPIView):
    input_class = ChangePasswordInput

    def post(self, request, *args, **kwargs):
        password_change.change_password(
            self.request.user, self.input.cleaned_data["new_password"]
        )
        is_set = not self.input.cleaned_data.get("current_password")
        if is_set:
            logged_out = password_change.finalize_password_set(request, request.user)
        else:
            logged_out = password_change.finalize_password_change(request, request.user)
        return response.respond_is_authenticated(
            request, is_authenticated=(not logged_out)
        )

    def get_input_kwargs(self):
        return {"user": self.request.user}


change_password = ChangePasswordView.as_view()


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
        data = [
            {
                "email": addr.email,
                "verified": addr.verified,
                "primary": addr.primary,
            }
            for addr in addrs
        ]
        return response.APIResponse(data=data)

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
        return response.APIResponse(
            {
                "verification_sent": sent,
            }
        )

    def get_input_kwargs(self):
        return {"user": self.request.user}


manage_email = ManageEmailView.as_view()


class ReauthenticateView(AuthenticatedAPIView):
    input_class = ReauthenticateInput

    def post(self, request, *args, **kwargs):
        flows.reauthentication.reauthenticate_by_password(self.request)
        return response.respond_is_authenticated(self.request)

    def get_input_kwargs(self):
        return {"user": self.request.user}


reauthenticate = ReauthenticateView.as_view()
