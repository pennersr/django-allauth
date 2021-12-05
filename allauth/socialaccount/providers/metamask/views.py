import json

from django.core.exceptions import ImproperlyConfigured

from allauth.socialaccount import app_settings, providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin
from django.http import HttpRequest
from .provider import MetamaskProvider


def metamask_login(request):
    accounts = request.POST.get("accounts", "")
    extra_data = json.dumps(accounts)
    request.account = accounts
    request.uid = request.POST.get("account","")
    request.settings = app_settings.PROVIDERS.get(MetamaskProvider.id, {})
    login = providers.registry.by_id(
        MetamaskProvider.id, request
    ).sociallogin_from_response(request, extra_data)
    login.state = SocialLogin.state_from_request(request)
    return complete_social_login(request, login)
