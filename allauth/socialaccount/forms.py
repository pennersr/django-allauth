from django import forms

from allauth.account.forms import BaseSignupForm
from allauth.socialaccount.internal import flows

from . import app_settings
from .adapter import get_adapter
from .models import SocialAccount


class SignupForm(BaseSignupForm):
    def __init__(self, *args, **kwargs):
        self.sociallogin = kwargs.pop("sociallogin")
        initial = get_adapter().get_signup_form_initial_data(self.sociallogin)
        kwargs.update(
            {
                "initial": initial,
                "email_required": kwargs.get(
                    "email_required", app_settings.EMAIL_REQUIRED
                ),
            }
        )
        super(SignupForm, self).__init__(*args, **kwargs)

    def save(self, request):
        adapter = get_adapter()
        user = adapter.save_user(request, self.sociallogin, form=self)
        self.custom_signup(request, user)
        return user

    def validate_unique_email(self, value):
        try:
            return super(SignupForm, self).validate_unique_email(value)
        except forms.ValidationError:
            raise get_adapter().validation_error(
                "email_taken", self.sociallogin.account.get_provider().name
            )


class DisconnectForm(forms.Form):
    account = forms.ModelChoiceField(
        queryset=SocialAccount.objects.none(),
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.accounts = SocialAccount.objects.filter(user=self.request.user)
        super(DisconnectForm, self).__init__(*args, **kwargs)
        self.fields["account"].queryset = self.accounts

    def clean(self):
        cleaned_data = super(DisconnectForm, self).clean()
        account = cleaned_data.get("account")
        if account:
            flows.connect.validate_disconnect(self.request, account)
        return cleaned_data

    def save(self):
        account = self.cleaned_data["account"]
        flows.connect.disconnect(self.request, account)
