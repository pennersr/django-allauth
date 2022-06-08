from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.utils.html import escapejs

from allauth.socialaccount.providers.base import (
    Provider,
    ProviderAccount,
    ProviderException,
)


class MetamaskAccount(ProviderAccount):
    def to_str(self):
        return self.account.uid


class MetamaskProvider(Provider):
    id = "metamask"
    name = "Metamask"
    account_class = MetamaskAccount

    def media_js(self, request):
        settings = self.get_settings()
        metamask_data = {
            "chainId": settings.get("CHAIN_ID", "0x1"),
            "chainName": settings.get("CHAIN_NAME", "mainnet"),
            "csrfToken": get_token(request),
            "rpcURL": settings.get("URL", "https://cloudflare-eth.com:8545/"),
        }
        ctx = {
            "metamask_data": metamask_data,
        }
        return render_to_string("metamask/auth.html", ctx, request=request)

    def get_login_url(self, request, **kwargs):
        next_url = "'%s'" % escapejs(kwargs.get("next") or "")
        process = "'%s'" % escapejs(kwargs.get("process") or "login")
        return "javascript:allauth.metamask.login(%s, %s)" % (next_url, process)

    def extract_common_fields(self, data):
        return dict(
            username=data.get("account"),
        )

    def extract_uid(self, data):
        if "account" not in data:
            raise ProviderException("metamask error", data)
        return str(data["account"])


provider_classes = [MetamaskProvider]
