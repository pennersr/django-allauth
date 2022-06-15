from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.urls import reverse
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

    def get_settings(self):
        ret = dict()
        ret.update(super().get_settings())
        ret.setdefault("CHAIN_ID", "0x1")
        ret.setdefault("CHAIN_METHOD", "wallet_switchEthereumChain")
        ret.setdefault("CHAIN_NAME", "mainnet")
        ret.setdefault("URL", "https://cloudflare-eth.com:8545/")
        return ret

    def media_js(self, request):
        settings = self.get_settings()
        metamask_data = {
            "chainId": settings["CHAIN_ID"],
            "chainMethod": settings["CHAIN_METHOD"],
            "chainName": settings["CHAIN_NAME"],
            "csrfToken": get_token(request),
            "nonceURL": reverse("metamask_nonce"),
            "verifyURL": reverse("metamask_verify"),
            "rpcURL": settings["URL"],
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
