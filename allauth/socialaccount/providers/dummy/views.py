from django.views.generic.base import View
from django.views.generic.edit import FormView

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.base.utils import respond_to_login_on_get
from allauth.socialaccount.providers.dummy.forms import AuthenticateForm
from allauth.socialaccount.providers.dummy.provider import DummyProvider


class LoginView(View):
    def dispatch(self, request, *args, **kwargs):
        provider = get_adapter().get_provider(request, DummyProvider.id)
        resp = respond_to_login_on_get(request, provider)
        if resp:
            return resp
        return provider.redirect_from_request(request)


login = LoginView.as_view()


class AuthenticateView(FormView):
    form_class = AuthenticateForm
    template_name = "dummy/authenticate_form.html"

    def form_valid(self, form):
        provider = get_adapter().get_provider(self.request, DummyProvider.id)
        login = provider.sociallogin_from_response(self.request, form.cleaned_data)
        login.state = SocialLogin.unstash_state(self.request)
        return complete_social_login(self.request, login)


authenticate = AuthenticateView.as_view()
