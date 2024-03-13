from types import SimpleNamespace

from django.middleware.csrf import get_token
from django.urls import reverse

from allauth import app_settings
from allauth.account.stages import LoginStageController
from allauth.headless.base import response
from allauth.headless.restkit.views import RESTView


class APIView(RESTView):
    def dispatch(self, request, *args, **kwargs):
        request.allauth.headless = SimpleNamespace()

        def headless_reverse(*args, **kwargs):
            kw = kwargs.setdefault("kwargs", {})
            kw["client"] = self.kwargs["client"]
            return reverse(*args, **kwargs)

        request.allauth.headless.client = self.kwargs["client"]
        request.allauth.headless.reverse = lambda *args, **kwargs: headless_reverse(
            *args, **kwargs
        )

        if request.allauth.headless.client == "browser":
            # Needed -- so that the CSRF token is set in the response for the
            # frontend to pick up.
            get_token(request)
        return super().dispatch(request, *args, **kwargs)


class AuthenticationStageAPIView(APIView):
    stage_class = None

    def handle(self, request, *args, **kwargs):
        self.stage = LoginStageController.enter(request, self.stage_class.key)
        if not self.stage:
            return response.UnauthorizedResponse(request)
        return super().handle(request, *args, **kwargs)

    def respond_stage_error(self):
        return response.UnauthorizedResponse(self.request)

    def respond_next_stage(self):
        self.stage.exit()
        return response.respond_is_authenticated(self.request)


class AuthenticatedAPIView(APIView):
    def handle(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return response.UnauthorizedResponse(request)
        return super().handle(request, *args, **kwargs)


class ConfigView(APIView):
    def get(self, request, *args, **kwargs):
        """
        The frontend queries (GET) this endpoint, expecting to receive
        either a 401 if no user is authenticated, or user information.
        """
        data = {}
        if app_settings.SOCIALACCOUNT_ENABLED:
            from allauth.headless.socialaccount.response import get_config_data

            data.update(get_config_data(request))
        if app_settings.MFA_ENABLED:
            from allauth.headless.mfa.response import get_config_data

            data.update(get_config_data(request))
        return response.APIResponse(data=data)


config = ConfigView.as_view()
