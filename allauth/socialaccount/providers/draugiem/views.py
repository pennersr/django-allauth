from hashlib import md5
import requests

from django.http import HttpResponseRedirect
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt

from allauth.compat import reverse
from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.helpers import render_authentication_error
from ..base import AuthError

from .provider import DraugiemProvider


class DraugiemApiError(Exception):
    pass


ACCESS_TOKEN_URL = 'http://api.draugiem.lv/json'
AUTHORIZE_URL = 'http://api.draugiem.lv/authorize'


def login(request):
    app = providers.registry.by_id(
        DraugiemProvider.id, request).get_app(request)
    request_scheme = request.META['wsgi.url_scheme']
    request_host = request.META['HTTP_HOST']
    request_path = reverse(callback)
    redirect_url = '%s://%s%s' % (request_scheme, request_host, request_path)
    redirect_url_hash = md5((
        app.secret + redirect_url).encode('utf-8')).hexdigest()
    params = {
        'app': app.client_id,
        'hash': redirect_url_hash,
        'redirect': redirect_url,
    }
    SocialLogin.stash_state(request)
    return HttpResponseRedirect('%s?%s' % (AUTHORIZE_URL, urlencode(params)))


@csrf_exempt
def callback(request):
    if 'dr_auth_status' not in request.GET:
        return render_authentication_error(
            request, DraugiemProvider.id, error=AuthError.UNKNOWN)

    if request.GET['dr_auth_status'] != 'ok':
        return render_authentication_error(
            request, DraugiemProvider.id, error=AuthError.DENIED)

    if 'dr_auth_code' not in request.GET:
        return render_authentication_error(
            request, DraugiemProvider.id, error=AuthError.UNKNOWN)

    ret = None
    auth_exception = None
    try:
        app = providers.registry.by_id(
            DraugiemProvider.id, request).get_app(request)
        login = draugiem_complete_login(
            request, app, request.GET['dr_auth_code'])
        login.state = SocialLogin.unstash_state(request)

        ret = complete_social_login(request, login)
    except (requests.RequestException, DraugiemApiError) as e:
        auth_exception = e

    if not ret:
        ret = render_authentication_error(
            request, DraugiemProvider.id, exception=auth_exception)

    return ret


def draugiem_complete_login(request, app, code):
    provider = providers.registry.by_id(DraugiemProvider.id, request)
    response = requests.get(ACCESS_TOKEN_URL, {
        'action': 'authorize',
        'app': app.secret,
        'code': code
    })
    response.raise_for_status()
    response_json = response.json()

    if 'error' in response_json:
        raise DraugiemApiError(response_json['error'])

    token = SocialToken(app=app, token=response_json['apikey'])

    login = provider.sociallogin_from_response(request, response_json)
    login.token = token
    return login
