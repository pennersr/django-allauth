from django import forms

from allauth.core import context
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.base.constants import AuthProcess


class RedirectToProviderForm(forms.Form):
    provider = forms.CharField()
    # FIXME: URLField? is_safe_url?
    callback_url = forms.CharField()
    process = forms.ChoiceField(
        choices=[
            (AuthProcess.LOGIN, AuthProcess.LOGIN),
            (AuthProcess.CONNECT, AuthProcess.CONNECT),
        ]
    )

    def clean_provider(self):
        provider_id = self.cleaned_data["provider"]
        provider = get_adapter().get_provider(context.request, provider_id)
        return provider
