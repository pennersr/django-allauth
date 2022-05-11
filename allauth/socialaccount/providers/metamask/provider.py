import json

from django.template.loader import render_to_string
from django.utils.html import escapejs

from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import Provider, ProviderAccount, ProviderException


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
        metamask_data = {
            "chainId": settings.get("CHAIN_ID",1 ),
            "RPC_URL": settings.get("URL", "https://cloudflare-eth.com/"),
            "PORT": settings.get("PORT",8545 ),
            "chainName": settings.get("CHAIN_NAME", "mainnet" ),
        }
        ctx = {"metamask_data": json.dumps(metamask_data),"request_parameters": json.dumps(request_parameters)}
        return render_to_string("metamask/auth.html", ctx, request=request)

    def get_login_url(self, request, **kwargs):
        next_url = "'%s'" % escapejs(kwargs.get("next") or "")
        process = "'%s'" % escapejs(kwargs.get("process") or "login")
        return "javascript:getAccount(%s, %s)" % (next_url, process)

    def extract_common_fields(self, data):
        return dict(
            username=data.get("account"),
        )

    def extract_uid(self, data):
        if 'account' not in data:
            raise ProviderException(
                'metamask error', data
            )
        return str(data['account'])

provider_classes = [MetamaskProvider]
