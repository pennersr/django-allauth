import json

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode

from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.base import Provider, ProviderAccount
from allauth.socialaccount.providers.dummy.forms import AuthenticateForm


class DummyAccount(ProviderAccount):
    pass


class DummyProvider(Provider):
    id = "dummy"
    name = "Dummy"
    account_class = DummyAccount
    uses_apps = False
    supports_redirect = True
    supports_token_authentication = True

    def get_login_url(self, request, **kwargs):
        url = reverse("dummy_login")
        if kwargs:
            url = url + "?" + urlencode(kwargs)
        return url

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        ret = {}
        if first_name := data.get("first_name"):
            ret["first_name"] = first_name
        if last_name := data.get("last_name"):
            ret["last_name"] = last_name
        if username := data.get("username"):
            ret["username"] = username
        if phone := data.get("phone"):
            ret["phone"] = phone
        if phone_verified := data.get("phone_verified"):
            ret["phone_verified"] = phone_verified
        return ret

    def redirect(self, request, process, next_url=None, data=None, **kwargs):
        state_id = self.stash_redirect_state(
            request,
            process,
            next_url=next_url,
            data=data,
            **kwargs,
        )
        return HttpResponseRedirect(
            reverse("dummy_authenticate") + "?" + urlencode({"state": state_id})
        )

    def extract_email_addresses(self, data):
        addresses = []
        email = data.get("email")
        if email:
            email_verified = data.get("email_verified")
            addresses.append(
                EmailAddress(
                    email=email,
                    verified=email_verified,
                    primary=True,
                )
            )
        return addresses

    def verify_token(self, request, token):
        # Our ID token is just a JSON payload that can be handed over
        # to the `AuthenticateForm`.
        id_token = token.get("id_token")
        if id_token:
            try:
                data = json.loads(id_token)
            except json.JSONDecodeError:
                pass
            else:
                form = AuthenticateForm(data=data)
                if form.is_valid():
                    return self.sociallogin_from_response(request, form.cleaned_data)
        raise get_adapter().validation_error("invalid_token")


provider_classes = [DummyProvider]
