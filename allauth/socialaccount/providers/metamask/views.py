import requests

from django.core.exceptions import ImproperlyConfigured

from allauth.socialaccount import app_settings, providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin

from .provider import MetamaskProvider


def metamask_login(request):
    assertion = request.POST.get("assertion", "")
    settings = app_settings.PROVIDERS.get(MetamaskProvider.id, {})
    try:
        resp.raise_for_status()
        extra_data = resp.json()
        if extra_data["status"] != "okay":
            return render_authentication_error(
                request,
                provider_id=MetamaskProvider.id,
                extra_context={"response": extra_data},
            )
    except (ValueError, requests.RequestException) as e:
        return render_authentication_error(
            request, provider_id=MetamaskProvider.id, exception=e
        )
    login = providers.registry.by_id(
        MetamaskProvider.id, request
    ).sociallogin_from_response(request, extra_data)
    login.state = SocialLogin.state_from_request(request)
    return complete_social_login(request, login)
