from allauth.headless.internal.restkit import inputs
from allauth.usersessions.models import UserSession


class SelectSessionsInput(inputs.Input):
    sessions = inputs.ModelMultipleChoiceField(queryset=UserSession.objects.none())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["sessions"].queryset = UserSession.objects.filter(user=self.user)
