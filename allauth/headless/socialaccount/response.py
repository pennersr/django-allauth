from allauth.socialaccount.adapter import (
    get_adapter as get_socialaccount_adapter,
)
from allauth.socialaccount.internal.flows import signup


def _serialize_provider(request, provider):
    return {
        "id": provider.id,
        "name": provider.name,
        "redirect_url": request.allauth.headless.reverse(
            "headless_redirect_to_provider",
        ),
    }


def provider_flows(request):
    flows = [_login_flow(request)]
    sociallogin = signup.get_pending_signup(request)
    if sociallogin:
        flows.append(_signup_flow(request, sociallogin))
    return flows


def _signup_flow(request, sociallogin):
    provider = sociallogin.account.get_provider()
    flow = {
        "id": "provider_signup",
        "url": request.allauth.headless.reverse("headless_provider_signup"),
        "provider": _serialize_provider(request, provider),
        "is_pending": True,
    }
    return flow


def _login_flow(request):
    flow = {
        "id": "provider_login",
        "url": request.allauth.headless.reverse("headless_redirect_to_provider"),
        "providers": [],
    }
    adapter = get_socialaccount_adapter()
    providers = adapter.list_providers(request)
    providers = sorted(providers, key=lambda p: p.name)
    for provider in providers:
        if not provider.supports_redirect:
            continue
        flow["providers"].append(_serialize_provider(request, provider))

    return flow
