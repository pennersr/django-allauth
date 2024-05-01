from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic.edit import FormView

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.base.constants import AuthError
from allauth.socialaccount.providers.base.views import BaseLoginView
from allauth.socialaccount.providers.dummy.forms import AuthenticateForm
from allauth.socialaccount.providers.dummy.provider import DummyProvider


class LoginView(BaseLoginView):
    provider_id = DummyProvider.id


login = LoginView.as_view()


class AuthenticateView(FormView):
    form_class = AuthenticateForm
    template_name = "dummy/authenticate_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.state_id = request.GET.get("state")
        if not self.state_id:
            raise PermissionDenied()
        self.provider = get_adapter().get_provider(self.request, DummyProvider.id)
        if request.method == "POST" and request.POST.get("action") == "cancel":
            return render_authentication_error(
                request,
                self.provider,
                error=AuthError.CANCELLED,
                extra_context={"state_id": self.state_id},
            )

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login = self.provider.sociallogin_from_response(self.request, form.cleaned_data)
        login.state = SocialLogin.unstash_state(self.request)
        return complete_social_login(self.request, login)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret["action_url"] = (
            reverse("dummy_authenticate") + "?" + urlencode({"state": self.state_id})
        )
        return ret


authenticate = AuthenticateView.as_view()
