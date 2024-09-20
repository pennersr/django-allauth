from allauth.account.stages import LoginStage
from allauth.core.internal.httpkit import headed_redirect_response


class PasskeySignupStage(LoginStage):
    # FIXME: requires headless support
    key = "mfa_webauthn_signup"
    urlname = "mfa_signup_webauthn"

    def handle(self):
        response, cont = None, True
        if self.login.state.get("passkey_signup"):
            response = headed_redirect_response("mfa_signup_webauthn")
        return response, cont
