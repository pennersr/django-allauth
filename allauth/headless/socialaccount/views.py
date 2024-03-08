from allauth.headless.base.views import APIView
from allauth.headless.socialaccount.forms import RedirectToProviderForm
from allauth.socialaccount.helpers import render_authentication_error


class ProviderSignUpView(APIView):
    pass


provider_signup = ProviderSignUpView.as_view()


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
