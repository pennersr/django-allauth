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
    account = request.POST.get("account", "")
    accounts = request.POST.get("accounts", "")
    next = request.POST.get("next", "")
    process = request.POST.get("process ", "")
    extra_data = accounts

    settings = app_settings.PROVIDERS.get(MetamaskProvider.id, {})
    login = providers.registry.by_id(
        MetamaskProvider.id, request
    ).sociallogin_from_response(request, extra_data)
    login.state = SocialLogin.state_from_request(request)
    return complete_social_login(request, login)
