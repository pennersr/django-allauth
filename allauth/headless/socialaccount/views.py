from allauth.headless.base.response import (
    APIResponse,
    respond_is_authenticated,
)
from allauth.headless.base.views import APIView, AuthenticatedAPIView
from allauth.headless.socialaccount.forms import RedirectToProviderForm
from allauth.headless.socialaccount.inputs import (
    DeleteProviderAccountInput,
    SignupInput,
)
from allauth.headless.socialaccount.response import serialize_socialaccount
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.internal import flows
from allauth.socialaccount.models import SocialAccount


class ProviderSignupView(APIView):
    input_class = SignupInput

    def post(self, request, *args, **kwargs):
        flows.signup.signup_by_form(self.request, self.sociallogin, self.input)
        return respond_is_authenticated(request)

    def get_input_kwargs(self):
        self.sociallogin = flows.signup.get_pending_signup(self.request)
        return {"sociallogin": self.sociallogin}


provider_signup = ProviderSignupView.as_view()


class RedirectToProviderView(APIView):
    handle_json_input = False

    def post(self, request, *args, **kwargs):
        form = RedirectToProviderForm(request.POST)
        if not form.is_valid():
            # TODO: Hand over form errors to render_authentication_error?
            return render_authentication_error(
                request, provider=request.POST.get("provider")
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


redirect_to_provider = RedirectToProviderView.as_view()


class ManageProvidersView(AuthenticatedAPIView):
    input_class = {
        "DELETE": DeleteProviderAccountInput,
    }

    def get(self, request, *args, **kwargs):
        return self._respond_provider_accounts()

    def _respond_provider_accounts(self):
        accounts = SocialAccount.objects.filter(user=self.request.user)
        data = [serialize_socialaccount(self.request, account) for account in accounts]
        return APIResponse(data=data)

    def delete(self, request, *args, **kwargs):
        flows.providers.disconnect(request, self.input.cleaned_data["account"])
        return self._respond_provider_accounts()

    def get_input_kwargs(self):
        return {"user": self.request.user}


manage_providers = ManageProvidersView.as_view()
