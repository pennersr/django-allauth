from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import FormView

from allauth.account.stages import LoginStageController
from allauth.mfa.forms import AuthenticateForm
from allauth.mfa.stages import AuthenticateStage


class AuthenticateView(FormView):
    form_class = AuthenticateForm
    template_name = "mfa/authenticate.html"

    def dispatch(self, request, *args, **kwargs):
        self.stage = LoginStageController.enter(request, AuthenticateStage.key)
        if not self.stage:
            return HttpResponseRedirect(reverse("account_login"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        return self.stage.exit()


authenticate = AuthenticateView.as_view()
