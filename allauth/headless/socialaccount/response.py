from allauth.headless.base.response import APIResponse
from allauth.headless.constants import Client
from allauth.socialaccount.adapter import (
    get_adapter as get_socialaccount_adapter,
)
from allauth.socialaccount.internal.flows import signup
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


def _serialize_provider(request, provider):
    ret = {
        "id": provider.id,
        "name": provider.name,
    }
    if isinstance(provider, OAuth2Provider):
        ret["client_id"] = provider.app.client_id
    return ret


def provider_flows(request):
    flows = []
    providers = _list_supported_providers(request)
    if providers:
        flows.append(_login_flow(request))
        sociallogin = signup.get_pending_signup(request)
        if sociallogin:
            flows.append(_signup_flow(request, sociallogin))
    return flows


def _signup_flow(request, sociallogin):
    provider = sociallogin.account.get_provider()
    flow = {
        "id": "provider_signup",
        "provider": _serialize_provider(request, provider),
        "is_pending": True,
    }
    return flow


def _login_flow(request):
    flow = {
        "id": "provider_login",
    }
    return flow


def _is_provider_supported(provider, client):
    if client == Client.APP:
        return provider.supports_token_authentication
    elif client == Client.BROWSER:
        return provider.supports_redirect
    return False


def _list_supported_providers(request):
    adapter = get_socialaccount_adapter()
    providers = adapter.list_providers(request)
    providers = [
        p
        for p in providers
        if _is_provider_supported(p, request.allauth.headless.client)
    ]
    return providers


def get_config_data(request):
    entries = []
    data = {"socialaccount": {"providers": entries}}
    providers = _list_supported_providers(request)
    providers = sorted(providers, key=lambda p: p.name)
    for provider in providers:
        entries.append(_serialize_provider(request, provider))
    return data


class SocialAccountsResponse(APIResponse):
    def __init__(self, request, accounts):
        data = [
            {
                "uid": account.uid,
                "provider": _serialize_provider(request, account.get_provider()),
                "display": account.get_provider_account().to_str(),
            }
            for account in accounts
        ]
        super().__init__(request, data=data)
