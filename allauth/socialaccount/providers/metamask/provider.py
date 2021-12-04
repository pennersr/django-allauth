import json

from django.template.loader import render_to_string
from django.utils.html import escapejs

from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import Provider, ProviderAccount


class MetamaskAccount(ProviderAccount):
    def to_str(self):
        return self.account.uid


class MetamaskProvider(Provider):
    id = "metamask"
    name = "Metamask"
    account_class = MetamaskAccount

    def media_js(self, request):
        settings = self.get_settings()
        request_parameters = settings.get("REQUEST_PARAMETERS", {})
        ctx = {"request_parameters": json.dumps(request_parameters)}
        return render_to_string("metamask/auth.html", ctx, request=request)

    def get_login_url(self, request, **kwargs):
        next_url = "'%s'" % escapejs(kwargs.get("next") or "")
        process = "'%s'" % escapejs(kwargs.get("process") or "login")
        return "javascript:getAccount(%s, %s)" % (next_url, process)

    def extract_uid(self, data):
        return data["username"]

provider_classes = [MetamaskProvider]
