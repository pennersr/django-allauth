from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import Provider, ProviderAccount
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlencode

rapidconnect_settings = getattr(settings, "SOCIALACCOUNT_PROVIDERS", {}).get("rapidconnect", {})
ATTRIBUTE_KEY = rapidconnect_settings.get("ATTRIBUTE_KEY", "https://aaf.edu.au/attributes")
BASE_URL = rapidconnect_settings.get("BASE_URL")
AUDIENCE = rapidconnect_settings.get("AUDIENCE")


class RapidConnectAccount(ProviderAccount):
    def to_str(self):
        data = self.account.extra_data

        cn = data.get("cn")
        displayname = data.get("displayname")
        first_name = data.get("givenname")
        last_name = data.get("surname")
        email = data.get("mail")

        if cn or displayname:
            return cn or displayname
        if first_name and last_name:
            return "%s %s" % (first_name, last_name)
        if email:
            return email
        return super(RapidConnectAccount, self).to_str()


class RapidConnectProvider(Provider):
    id = "rapidconnect"
    name = "RapidConnect"
    account_class = RapidConnectAccount

    def get_login_url(self, request, **kwargs):
        url = reverse(self.id + "_login")
        if kwargs:
            url = url + "?" + urlencode(kwargs)
        return url

    def extract_uid(self, data):
        return str(data.get("edupersonprincipalname") or data.get("mail"))

    def extract_common_fields(self, data):
        cn = data.get("cn")
        displayname = data.get("displayname")
        surname = data.get("surname")
        givenname = data.get("givenname")
        email = data.get("mail")
        orcid = data.get("edupersonorcid")
        # edupersonprincipalname = data.get("edupersonprincipalname")
        # edupersonscopedaffiliation = data.get("edupersonscopedaffiliation")

        return dict(
            name=cn or displayname,
            first_name=givenname,
            last_name=surname,
            email=email,
            orcid=orcid,
        )

    def extract_email_addresses(self, data):
        email = data.get("mail")
        if email:
            return [EmailAddress(email=email, verified=True, primary=True)]
        return []

    def cleanup_email_addresses(self, email, addresses):
        # Move user.email over to EmailAddress
        if email and email.lower() not in [a.email.lower() for a in addresses]:
            addresses.append(EmailAddress(email=email, verified=False, primary=True))

    def extract_extra_data(self, data):
        return data


provider_classes = [RapidConnectProvider]
