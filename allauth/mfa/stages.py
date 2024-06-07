from django.http import HttpResponseRedirect, HttpResponseServerError
from django.urls import NoReverseMatch, reverse

from allauth import app_settings as allauth_settings
from allauth.account.stages import LoginStage
from allauth.mfa.models import Authenticator
from allauth.mfa.utils import is_mfa_enabled


class AuthenticateStage(LoginStage):
    key = "mfa_authenticate"

    def handle(self):
        response, cont = None, True
        if is_mfa_enabled(
            self.login.user, [Authenticator.Type.TOTP, Authenticator.Type.WEBAUTHN]
        ):
            try:
                response = HttpResponseRedirect(reverse("mfa_authenticate"))
            except NoReverseMatch:
                if allauth_settings.HEADLESS_ONLY:
                    # The response we would be rendering here is not actually used.
                    response = HttpResponseServerError()
                else:
                    raise
        return response, cont
