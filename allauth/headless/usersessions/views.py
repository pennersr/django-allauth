from allauth.headless.base.response import AuthenticationResponse
from allauth.headless.base.views import AuthenticatedAPIView
from allauth.headless.usersessions.inputs import SelectSessionsInput
from allauth.headless.usersessions.response import SessionsResponse
from allauth.usersessions.internal import flows
from allauth.usersessions.models import UserSession


class SessionsView(AuthenticatedAPIView):
    input_class = {"DELETE": SelectSessionsInput}

    def delete(self, request, *args, **kwargs):
        sessions = self.input.cleaned_data["sessions"]
        flows.sessions.end_sessions(request, sessions)
        if self.request.user.is_authenticated:
            return self._respond_session_list()
        return AuthenticationResponse(request)

    def get(self, request, *args, **kwargs):
        return self._respond_session_list()

    def _respond_session_list(self):
        sessions = UserSession.objects.purge_and_list(self.request.user)
        return SessionsResponse(self.request, sessions)

    def get_input_kwargs(self):
        return {"user": self.request.user}
