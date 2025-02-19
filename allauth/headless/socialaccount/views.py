from django.core.exceptions import ValidationError

from allauth.core.exceptions import SignupClosedException
from allauth.headless.base.response import (
    AuthenticationResponse,
    ConflictResponse,
    ForbiddenResponse,
)
from allauth.headless.base.views import APIView, AuthenticatedAPIView
from allauth.headless.internal.restkit.response import ErrorResponse
from allauth.headless.socialaccount.forms import RedirectToProviderForm
from allauth.headless.socialaccount.inputs import (
    DeleteProviderAccountInput,
    ProviderTokenInput,
    SignupInput,
)
from allauth.headless.socialaccount.internal import complete_token_login
from allauth.headless.socialaccount.response import (
    SocialAccountsResponse,
    SocialLoginResponse,
)
from allauth.socialaccount.adapter import (
    get_adapter as get_socialaccount_adapter,
)
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.internal import flows
from allauth.socialaccount.models import SocialAccount


class ProviderSignupView(APIView):
    input_class = SignupInput

    def handle(self, request, *args, **kwargs):
        self.sociallogin = flows.signup.get_pending_signup(self.request)
        if not self.sociallogin:
            return ConflictResponse(request)
        if not get_socialaccount_adapter().is_open_for_signup(
            request, self.sociallogin
        ):
            return ForbiddenResponse(request)
        return super().handle(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return SocialLoginResponse(request, self.sociallogin)

    def post(self, request, *args, **kwargs):
        response = flows.signup.signup_by_form(
            self.request, self.sociallogin, self.input
        )
        return AuthenticationResponse.from_response(request, response)

    def get_input_kwargs(self):
        return {"sociallogin": self.sociallogin}


class RedirectToProviderView(APIView):
    handle_json_input = False

    def post(self, request, *args, **kwargs):
        form = RedirectToProviderForm(request.POST)
        if not form.is_valid():
            return render_authentication_error(
                request,
                provider=request.POST.get("provider"),
                exception=ValidationError(form.errors),
            )
        provider = form.cleaned_data["provider"]
        next_url = form.cleaned_data["callback_url"]
        process = form.cleaned_data["process"]
        return provider.redirect(
            request,
            process,
            next_url=next_url,
            headless=True,
        )


class ManageProvidersView(AuthenticatedAPIView):
    input_class = {
        "DELETE": DeleteProviderAccountInput,
    }

    def get(self, request, *args, **kwargs):
        return self.respond_provider_accounts(request)

    @classmethod
    def respond_provider_accounts(self, request):
        accounts = SocialAccount.objects.filter(user=request.user)
        return SocialAccountsResponse(request, accounts)

    def delete(self, request, *args, **kwargs):
        flows.connect.disconnect(request, self.input.cleaned_data["account"])
        return self.respond_provider_accounts(request)

    def get_input_kwargs(self):
        return {"user": self.request.user}


class ProviderTokenView(APIView):
    input_class = ProviderTokenInput

    def post(self, request, *args, **kwargs):
        sociallogin = self.input.cleaned_data["sociallogin"]
        response = None
        try:
            response = complete_token_login(request, sociallogin)
        except ValidationError as e:
            return ErrorResponse(self.request, exception=e)
        except SignupClosedException:
            return ForbiddenResponse(self.request)
        return AuthenticationResponse.from_response(self.request, response)
