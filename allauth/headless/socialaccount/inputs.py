from django.core.exceptions import ValidationError

from allauth.core import context
from allauth.headless.adapter import get_adapter
from allauth.headless.internal.restkit import inputs
from allauth.socialaccount.adapter import (
    get_adapter as get_socialaccount_adapter,
)
from allauth.socialaccount.forms import SignupForm
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.base.constants import AuthProcess


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
                raise get_adapter().validation_error("account_not_found")
            get_socialaccount_adapter().validate_disconnect(account, accounts)
            self.cleaned_data["account"] = account
        return cleaned_data


class ProviderTokenInput(inputs.Input):
    provider = inputs.CharField()
    process = inputs.ChoiceField(
        choices=[
            (AuthProcess.LOGIN, AuthProcess.LOGIN),
            (AuthProcess.CONNECT, AuthProcess.CONNECT),
        ]
    )
    token = inputs.Field()

    def clean(self):
        cleaned_data = super().clean()
        token = self.data.get("token")
        adapter = get_adapter()
        client_id = None
        if not isinstance(token, dict):
            self.add_error("token", adapter.validation_error("invalid_token"))
            token = None
        else:
            client_id = token.get("client_id")
            if not isinstance(client_id, str):
                self.add_error("token", adapter.validation_error("client_id_required"))
                client_id = None

        provider_id = cleaned_data.get("provider")
        provider = None
        if provider_id and token and client_id:
            provider = get_socialaccount_adapter().get_provider(
                context.request, provider_id, client_id=client_id
            )
            if not provider.supports_token_authentication:
                self.add_error(
                    "provider",
                    adapter.validation_error("token_authentication_not_supported"),
                )

            elif provider.app.client_id != client_id:
                self.add_error("token", adapter.validation_error("client_id_mismatch"))
            else:
                id_token = token.get("id_token")
                access_token = token.get("access_token")
                if (
                    (id_token is not None and not isinstance(id_token, str))
                    or (access_token is not None and not isinstance(access_token, str))
                    or (not id_token and not access_token)
                ):
                    self.add_error("token", adapter.validation_error("token_required"))
        if not self.errors:
            cleaned_data["provider"] = provider
            try:
                login = provider.verify_token(context.request, token)
                login.state["process"] = cleaned_data["process"]
                cleaned_data["sociallogin"] = login
            except ValidationError as e:
                self.add_error("token", e)
        return cleaned_data
