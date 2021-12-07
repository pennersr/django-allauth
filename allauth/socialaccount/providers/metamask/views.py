import json
from django.http import JsonResponse
import web3 as Web3
import random
import string
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import logout

from allauth.socialaccount import app_settings, providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin, SocialToken
from django.http import HttpRequest
from .provider import MetamaskProvider
from django.views.decorators.http import require_http_methods


def metamask_nonce(request):
    extra_data = json.loads(request.body)
    request.settings = app_settings.PROVIDERS.get(MetamaskProvider.id, {})
    provider = providers.registry.by_id(MetamaskProvider.id, request)
    app = provider.get_app(request)
    expires_at = None
    token = SocialToken(
        app=app, token=extra_data, expires_at=expires_at
    )
    return JsonResponse(token.token, safe=False)

def metamask_login(request):
    extra_data = json.loads(request.body)
    request.uid = request.POST.get("account","")
    request.settings = app_settings.PROVIDERS.get(MetamaskProvider.id, {})
    # Verify token signed here, and if so use the nonce to log in.

    login = providers.registry.by_id(
        MetamaskProvider.id, request
    ).sociallogin_from_response(request, extra_data)
    login.state = SocialLogin.state_from_request(request)
    return complete_social_login(request, login)

@require_http_methods(["GET", "POST"])
def login_api(request):
    extra_data = request.body.decode('utf-8')
    data = json.loads(extra_data)
    request.uid = data["account"]
    request.process = data["process"]
    request.settings = app_settings.PROVIDERS.get(MetamaskProvider.id, {})
    provider = providers.registry.by_id(MetamaskProvider.id, request)
    if request.process == 'token':
        token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(32))
        request.session['login_token'] = token
        app = provider.get_app(request)
        expires_at = None
        storetoken = SocialToken(
            app=app, token=token, expires_at=expires_at
        )
        login = providers.registry.by_id(MetamaskProvider.id, request).sociallogin_from_response(request, data)
        login.state = SocialLogin.state_from_request(request)
        login.token = storetoken
        complete_social_login(request, login)
        logout(request)
        return JsonResponse({'data': token, 'success': True },safe=False)
    else:
        token = request.session.get('login_token')
        if not token:
            return JsonResponse({'error': _(
                "No login token in session, please request token again by sending request to this url"),
                'success': False})
        else:
            login = providers.registry.by_id(MetamaskProvider.id, request).sociallogin_from_response(request, data)
            login.state = SocialLogin.state_from_request(request)
            local_token = login.token
            url = provider.get_settings().get("url")
            port = provider.get_settings().get("port")
            endpoint = url+':'+ str(port)
            w3 = Web3(Web3.HTTPProvider(endpoint))
            encoded_message = encode_defunct(bytes(local_token, encoding='utf8'))
            recoveredAddress = w3.eth.account.recover_message(encoded_message, data["login_token"])
            if recoveredAddress == data['account']:
                return complete_social_login(request, login)
            else:
                return logout(request)
