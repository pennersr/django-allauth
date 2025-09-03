from allauth.account.stages import LoginStage
from allauth.core.internal.httpkit import headed_redirect_response
from allauth.mfa.internal.constants import LoginStageKey


class PasskeySignupStage(LoginStage):
    key = LoginStageKey.MFA_SIGNUP_WEBAUTHN.value
    urlname = "mfa_signup_webauthn"

    def handle(self):
        response, cont = None, True
        if self.login.state.get("passkey_signup"):
            response = headed_redirect_response("mfa_signup_webauthn")
        return response, cont
