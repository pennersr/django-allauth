import json
from django.http import JsonResponse
import random
import string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect


from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import logout

from allauth.socialaccount import app_settings, providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin, SocialToken
from .provider import MetamaskProvider
from django.views.decorators.http import require_http_methods

# web3 declarations
from web3 import Web3
from eth_account.messages import encode_defunct
from django.utils.translation import ugettext_lazy as _

@csrf_exempt
@require_http_methods(["GET","POST"])
def login_api(request):
    extra_data = request.body.decode('utf-8')
    data = json.loads(extra_data)
    request.uid = data["account"]
    request.process = data["process"]
    if "login_token" in data.keys():
        request.session['login_token'] = data["login_token"]
    settings = app_settings.PROVIDERS.get(MetamaskProvider.id, {})
    provider = providers.registry.by_id(MetamaskProvider.id, request)
    url = settings.get("URL", "https://cloudflare-eth.com/")
    port = settings.get("PORT", 80 )
    w3 = Web3(Web3.HTTPProvider(url+':'+str(port)))
    if request.process == 'token':
        token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(32))
        request.session['login_token'] = token
        app = provider.get_app(request)
        expires_at = None
        SocialToken.objects.all().filter(account__uid=data["account"], account__provider=MetamaskProvider.id).delete()
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
            local = SocialToken.objects.all().filter(account__uid=data["account"],account__provider=MetamaskProvider.id).first()
            message_hash = encode_defunct(text=local.token)
            recoveredAddress = w3.eth.account.recover_message(message_hash, signature=data['login_token'])
            request.session['login_token'] = token
            if recoveredAddress.upper() == data['account'].upper():
                login = providers.registry.by_id(MetamaskProvider.id, request).sociallogin_from_response(request, data)
                login.state = SocialLogin.state_from_request(request)
                complete_social_login(request, login)
                return redirect(data["next"])
            return JsonResponse({'error': _(
                "The signature could not be verified. "),
                'success': False})
