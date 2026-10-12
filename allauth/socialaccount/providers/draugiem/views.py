from __future__ import annotations

import requests

from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from allauth.account.internal.decorators import login_not_required
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.internal import statekit
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.base.views import BaseLoginView
from allauth.socialaccount.providers.draugiem.provider import DraugiemProvider

from ..base import AuthError


class DraugiemApiError(Exception):
    pass


ACCESS_TOKEN_URL = "https://api.draugiem.lv/json"  # nosec


@method_decorator(login_not_required, name="dispatch")
class LoginView(BaseLoginView):
    provider_id = DraugiemProvider.id


login = LoginView.as_view()


@csrf_exempt
def callback(request: HttpRequest):
    adapter = get_adapter()
    provider = adapter.get_provider(request, DraugiemProvider.id)

    if "dr_auth_status" not in request.GET:
        return render_authentication_error(request, provider, error=AuthError.UNKNOWN)

    if request.GET["dr_auth_status"] != "ok":
        return render_authentication_error(request, provider, error=AuthError.DENIED)

    if "dr_auth_code" not in request.GET:
        return render_authentication_error(request, provider, error=AuthError.UNKNOWN)

    ret = None
    auth_exception = None
    try:
        app = provider.app
        login = draugiem_complete_login(request, app, request.GET["dr_auth_code"])
        login.state = statekit.unstash_last_state(
            request, provider_id=provider.sub_id, raises=True
        )

        ret = complete_social_login(request, login)
    except (requests.RequestException, DraugiemApiError) as e:
        auth_exception = e

    if not ret:
        ret = render_authentication_error(request, provider, exception=auth_exception)

    return ret


def draugiem_complete_login(request: HttpRequest, app, code):
    provider = get_adapter().get_provider(request, DraugiemProvider.id)
    with get_adapter().get_requests_session() as sess:
        params = {"action": "authorize", "app": app.secret, "code": code}
        response = sess.get(ACCESS_TOKEN_URL, params=params)
        response.raise_for_status()
        response_json = response.json()

    if "error" in response_json:
        raise DraugiemApiError(response_json["error"])

    token = SocialToken(app=app, token=response_json["apikey"])

    login = provider.sociallogin_from_response(request, response_json)
    login.token = token
    return login
