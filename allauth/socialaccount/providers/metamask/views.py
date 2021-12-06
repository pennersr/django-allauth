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
    if request.method == 'GET':
        token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(32))
        request.session['login_token'] = token
        return JsonResponse({'data': token, 'success': True})
    else:
        token = request.session.get('login_token')
        if not token:
            return JsonResponse({'error': _(
                "No login token in session, please request token again by sending GET request to this url"),
                'success': False})
        else:
            form = LoginForm(token, request.POST)
            if form.is_valid():
                signature, address = form.cleaned_data.get("signature"), form.cleaned_data.get("address")
                del request.session['login_token']
                user = authenticate(request, token=token, address=address, signature=signature)
                if user:
                    login(request, user, 'web3auth.backend.Web3Backend')

                    return JsonResponse({'success': True, 'redirect_url': get_redirect_url(request)})
                else:
                    error = _("Can't find a user for the provided signature with address {address}").format(
                        address=address)
                    return JsonResponse({'success': False, 'error': error})
            else:
                return JsonResponse({'success': False, 'error': json.loads(form.errors.as_json())})
