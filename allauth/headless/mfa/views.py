from allauth.headless.base.views import AuthenticationStageAPIView
from allauth.headless.mfa.inputs import AuthenticateInput
from allauth.mfa.stages import AuthenticateStage


class AuthenticateView(AuthenticationStageAPIView):
    input_class = AuthenticateInput
    stage_class = AuthenticateStage

    def post(self, request, *args, **kwargs):
        self.input.save()
        return self.respond_next_stage()

    def get_input_kwargs(self):
        return {"user": self.stage.login.user}


authenticate = AuthenticateView.as_view()
