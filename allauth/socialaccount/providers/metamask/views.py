import json
from django.http import JsonResponse
import web3

from django.core.exceptions import ImproperlyConfigured

from allauth.socialaccount import app_settings, providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin, SocialToken
from django.http import HttpRequest
from .provider import MetamaskProvider

def metamask_nonce(request):
    extra_data = json.loads(request.body)
    request.settings = app_settings.PROVIDERS.get(MetamaskProvider.id, {})
    provider = providers.registry.by_id(MetamaskProvider.id, request)
    app = 'metamask'
    expires_at = None
    nonce = secrets.token_urlsafe()
    token = SocialToken(
        app=app, token=extra_data, expires_at=expires_at
    )
    return JsonResponse(token, safe=False)

def metamask_login(request):
    extra_data = json.loads(request.body)

    request.uid = request.POST.get("account","")
    request.settings = app_settings.PROVIDERS.get(MetamaskProvider.id, {})
    login = providers.registry.by_id(
        MetamaskProvider.id, request
    ).sociallogin_from_response(request, extra_data)
    login.state = SocialLogin.state_from_request(request)
    return complete_social_login(request, login)
