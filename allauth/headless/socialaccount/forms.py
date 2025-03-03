from django import forms
from django.core.exceptions import ObjectDoesNotExist

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.core import context
from allauth.headless.adapter import get_adapter
from allauth.socialaccount.adapter import (
    get_adapter as get_socialaccount_adapter,
)
from allauth.socialaccount.providers.base.constants import AuthProcess


class RedirectToProviderForm(forms.Form):
    provider = forms.CharField()
    callback_url = forms.CharField()
    process = forms.ChoiceField(
        choices=[
            (AuthProcess.LOGIN, AuthProcess.LOGIN),
            (AuthProcess.CONNECT, AuthProcess.CONNECT),
        ]
    )

    def clean_callback_url(self):
        url = self.cleaned_data["callback_url"]
        if not get_account_adapter().is_safe_url(url):
            raise get_adapter().validation_error("invalid_url")
        return url

    def clean_provider(self):
        provider_id = self.cleaned_data["provider"]
        try:
            provider = get_socialaccount_adapter().get_provider(
                context.request, provider_id
            )
        except ObjectDoesNotExist:
            raise get_adapter().validation_error("unknown_provider")
        return provider
