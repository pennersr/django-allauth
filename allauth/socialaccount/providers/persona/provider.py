import json

from django.template.loader import render_to_string
from django.utils.html import escapejs

from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import Provider, ProviderAccount


class PersonaAccount(ProviderAccount):
    def to_str(self):
        return self.account.uid


class PersonaProvider(Provider):
    id = "persona"
    name = "Persona"
    account_class = PersonaAccount

    def media_js(self, request):
        settings = self.get_settings()
        request_parameters = settings.get("REQUEST_PARAMETERS", {})
        ctx = {"request_parameters": json.dumps(request_parameters)}
        return render_to_string("persona/auth.html", ctx, request=request)

    def get_login_url(self, request, **kwargs):
        next_url = "'%s'" % escapejs(kwargs.get("next") or "")
        process = "'%s'" % escapejs(kwargs.get("process") or "login")
        return "javascript:allauth.persona.login(%s, %s)" % (next_url, process)

    def extract_uid(self, data):
        return data["email"]

    def extract_common_fields(self, data):
        return dict(email=data["email"])

    def extract_email_addresses(self, data):
        ret = [EmailAddress(email=data["email"], verified=True, primary=True)]
        return ret


provider_classes = [PersonaProvider]
