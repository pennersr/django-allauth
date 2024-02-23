from django.http import HttpResponseRedirect
from django.urls import reverse

from allauth.account.stages import LoginStage
from allauth.mfa.utils import is_mfa_enabled


class AuthenticateStage(LoginStage):
    key = "mfa_authenticate"

    def handle(self):
        response, cont = None, True
        if is_mfa_enabled(self.login.user):
            response = HttpResponseRedirect(reverse("mfa_authenticate"))
        return response, cont

    def get_headless_url(self):
        return self.request.allauth.headless.reverse("headless_mfa_authenticate")
