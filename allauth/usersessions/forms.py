from django import forms
from django.http import HttpRequest

from allauth.usersessions.internal import flows


class ManageUserSessionsForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def save(self, request: HttpRequest) -> None:
        if request.user.is_authenticated:
            flows.sessions.end_other_sessions(request, request.user)
