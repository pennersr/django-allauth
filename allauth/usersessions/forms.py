from django import forms

from allauth.usersessions.internal import flows


class ManageUserSessionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def save(self, request):
        flows.sessions.end_other_sessions(request, request.user)
