from django import forms

from allauth.mfa.adapter import get_adapter
from allauth.mfa.recovery_codes.internal import flows


class GenerateRecoveryCodesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not flows.can_generate_recovery_codes(self.user):
            raise get_adapter().validation_error("cannot_generate_recovery_codes")
        return cleaned_data
