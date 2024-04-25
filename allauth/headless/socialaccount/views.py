from django.core.exceptions import ValidationError

from allauth.headless.base.response import AuthenticationResponse
from allauth.headless.base.views import APIView, AuthenticatedAPIView
from allauth.headless.socialaccount.forms import RedirectToProviderForm
from allauth.headless.socialaccount.inputs import (
    DeleteProviderAccountInput,
    ProviderTokenInput,
    SignupInput,
)
from allauth.headless.socialaccount.internal import complete_login
from allauth.headless.socialaccount.response import SocialAccountsResponse
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.internal import flows
from allauth.socialaccount.models import SocialAccount


class ProviderSignupView(APIView):
    input_class = SignupInput

    def post(self, request, *args, **kwargs):
        flows.signup.signup_by_form(self.request, self.sociallogin, self.input)
        return AuthenticationResponse(request)

    def get_input_kwargs(self):
        self.sociallogin = flows.signup.get_pending_signup(self.request)
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
        complete_login(request, sociallogin)
        return AuthenticationResponse(self.request)
