from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode

from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import Provider, ProviderAccount


class DummyAccount(ProviderAccount):
    def to_str(self):
        dflt = super().to_str()
        first_name = self.account.extra_data.get("first_name") or ""
        last_name = self.account.extra_data.get("last_name") or ""
        name = " ".join([first_name, last_name]).strip() or dflt
        return name


class DummyProvider(Provider):
    id = "dummy"
    name = "Dummy"
    account_class = DummyAccount
    uses_apps = False
    supports_redirect = True

    def get_login_url(self, request, **kwargs):
        url = reverse("dummy_login")
        if kwargs:
            url = url + "?" + urlencode(kwargs)
        return url

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        ret = {}
        if data.get("first_name"):
            ret["first_name"] = data.get("first_name")
        if data.get("last_name"):
            ret["last_name"] = data.get("last_name")
        if data.get("username"):
            ret["username"] = data.get("username")
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


provider_classes = [DummyProvider]
