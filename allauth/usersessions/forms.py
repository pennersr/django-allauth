from django import forms

from allauth.usersessions.adapter import get_adapter
from allauth.usersessions.models import UserSession


class ManageUserSessionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def save(self, request):
        sessions_to_end = []
        for session in UserSession.objects.filter(user=request.user):
            if session.is_current():
                continue
            sessions_to_end.append(session)
        get_adapter().end_sessions(sessions_to_end)
