from __future__ import annotations

from allauth.headless.internal.restkit import inputs
from allauth.usersessions.models import UserSession


class SelectSessionsInput(inputs.Input):
    sessions = inputs.ModelMultipleChoiceField(queryset=UserSession.objects.none())

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        sessions_field: inputs.ModelMultipleChoiceField = self.fields["sessions"]  # type: ignore[assignment]
        sessions_field.queryset = UserSession.objects.filter(user=self.user)
