from allauth.headless.account.response import email_address_data
from allauth.headless.adapter import get_adapter
from allauth.headless.base.response import APIResponse
from allauth.headless.constants import Client, Flow
from allauth.socialaccount.adapter import (
    get_adapter as get_socialaccount_adapter,
)
from allauth.socialaccount.internal.flows import signup
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


def _socialaccount_data(request, account):
    return {
        "uid": account.uid,
        "provider": _provider_data(request, account.get_provider()),
        "display": account.get_provider_account().to_str(),
    }


def _provider_data(request, provider):
    ret = {"id": provider.sub_id, "name": provider.name, "flows": []}
    if provider.supports_redirect:
        ret["flows"].append(Flow.PROVIDER_REDIRECT)
    if provider.supports_token_authentication:
        ret["flows"].append(Flow.PROVIDER_TOKEN)
    if isinstance(provider, OAuth2Provider):
        ret["client_id"] = provider.app.client_id
        if provider.id == "openid_connect":
            ret["openid_configuration_url"] = provider.server_url

    return ret


def provider_flows(request):
    flows = []
    providers = _list_supported_providers(request)
    if providers:
        redirect_providers = [p.sub_id for p in providers if p.supports_redirect]
        token_providers = [
            p.sub_id for p in providers if p.supports_token_authentication
        ]
        if redirect_providers and request.allauth.headless.client == Client.BROWSER:
            flows.append(
                {
                    "id": Flow.PROVIDER_REDIRECT,
                    "providers": redirect_providers,
                }
            )
        if token_providers:
            flows.append(
                {
                    "id": Flow.PROVIDER_TOKEN,
                    "providers": token_providers,
                }
            )
        sociallogin = signup.get_pending_signup(request)
        if sociallogin:
            flows.append(_signup_flow(request, sociallogin))
    return flows


def _signup_flow(request, sociallogin):
    provider = sociallogin.provider
    flow = {
        "id": Flow.PROVIDER_SIGNUP,
        "provider": _provider_data(request, provider),
        "is_pending": True,
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
        entries.append(_provider_data(request, provider))
    return data


class SocialAccountsResponse(APIResponse):
    def __init__(self, request, accounts):
        data = [_socialaccount_data(request, account) for account in accounts]
        super().__init__(request, data=data)


class SocialLoginResponse(APIResponse):
    def __init__(self, request, sociallogin):
        adapter = get_adapter()
        data = {
            "user": adapter.serialize_user(sociallogin.user),
            "account": _socialaccount_data(request, sociallogin.account),
            "email": [email_address_data(ea) for ea in sociallogin.email_addresses],
        }
        super().__init__(request, data=data)
