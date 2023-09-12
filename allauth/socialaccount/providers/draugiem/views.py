import requests
from hashlib import md5

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin, SocialToken

from ..base import AuthError
from .provider import DraugiemProvider


class DraugiemApiError(Exception):
    pass


ACCESS_TOKEN_URL = "http://api.draugiem.lv/json"
AUTHORIZE_URL = "http://api.draugiem.lv/authorize"


def login(request):
    app = get_adapter().get_app(request, DraugiemProvider.id)
    redirect_url = request.build_absolute_uri(reverse(callback))
    redirect_url_hash = md5((app.secret + redirect_url).encode("utf-8")).hexdigest()
    params = {
        "app": app.client_id,
        "hash": redirect_url_hash,
        "redirect": redirect_url,
    }
    SocialLogin.stash_state(request)
    return HttpResponseRedirect("%s?%s" % (AUTHORIZE_URL, urlencode(params)))


@csrf_exempt
def callback(request):
    if "dr_auth_status" not in request.GET:
        return render_authentication_error(
            request, DraugiemProvider.id, error=AuthError.UNKNOWN
        )

    if request.GET["dr_auth_status"] != "ok":
        return render_authentication_error(
            request, DraugiemProvider.id, error=AuthError.DENIED
        )

    if "dr_auth_code" not in request.GET:
        return render_authentication_error(
            request, DraugiemProvider.id, error=AuthError.UNKNOWN
        )

    ret = None
    auth_exception = None
    try:
        app = get_adapter().get_app(request, DraugiemProvider.id)
        login = draugiem_complete_login(request, app, request.GET["dr_auth_code"])
        login.state = SocialLogin.unstash_state(request)

        ret = complete_social_login(request, login)
    except (requests.RequestException, DraugiemApiError) as e:
        auth_exception = e

    if not ret:
        ret = render_authentication_error(
            request, DraugiemProvider.id, exception=auth_exception
        )

    return ret


def draugiem_complete_login(request, app, code):
    provider = get_adapter().get_provider(request, DraugiemProvider.id)
    response = requests.get(
        ACCESS_TOKEN_URL,
        {"action": "authorize", "app": app.secret, "code": code},
    )
    response.raise_for_status()
    response_json = response.json()

    if "error" in response_json:
        raise DraugiemApiError(response_json["error"])

    token = SocialToken(app=app, token=response_json["apikey"])

    login = provider.sociallogin_from_response(request, response_json)
    login.token = token
    return login
