from allauth.headless.base.response import respond_is_authenticated
from allauth.headless.base.views import APIView
from allauth.headless.socialaccount.forms import RedirectToProviderForm
from allauth.headless.socialaccount.inputs import SignupInput
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.internal import flows


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
                request, provider=request.POST.get("provider_id")
            )
        provider = form.cleaned_data["provider_id"]
        next_url = form.cleaned_data["callback_url"]
        process = form.cleaned_data["process"]
        return provider.redirect(
            request,
            process,
            next_url=next_url,
            state={
                "headless": True,
            },
        )


redirect_to_provider = RedirectToProviderView.as_view()
