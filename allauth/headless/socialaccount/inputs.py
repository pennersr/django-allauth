from allauth.headless.restkit import inputs
from allauth.socialaccount.adapter import (
    get_adapter as get_socialaccount_adapter,
)
from allauth.socialaccount.forms import SignupForm
from allauth.socialaccount.models import SocialAccount


class SignupInput(SignupForm, inputs.Input):
    pass


class DeleteProviderAccountInput(inputs.Input):
    provider = inputs.CharField()
    account = inputs.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        uid = cleaned_data.get("account")
        provider_id = cleaned_data.get("provider")
        if uid and provider_id:
            accounts = SocialAccount.objects.filter(user=self.user)
            account = accounts.filter(
                uid=uid,
                provider=provider_id,
            ).first()
            if not account:
                raise inputs.ValidationError("Unknown account.")
            get_socialaccount_adapter().validate_disconnect(account, accounts)
            self.cleaned_data["account"] = account
        return cleaned_data
