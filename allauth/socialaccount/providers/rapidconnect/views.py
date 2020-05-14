import requests
from hashlib import md5
from urllib.parse import urljoin
import jwt

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt

from allauth.socialaccount import providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.socialaccount.providers.base import AuthError

from .provider import ATTRIBUTE_KEY, AUDIENCE, BASE_URL, RapidConnectProvider


class RapidConnectApiError(Exception):
    pass


def login(request):
    app = providers.registry.by_id(RapidConnectProvider.id, request).get_app(request)
    url = app.client_id
    if BASE_URL:
        url = urljoin(BASE_URL, url)
        # request.build_absolute_uri()

    SocialLogin.stash_state(request)
    return HttpResponseRedirect(url)


@csrf_exempt
def callback(request):

    # if "dr_auth_status" not in request.GET:
    #     return render_authentication_error(
    #         request, RapidConnectProvider.id, error=AuthError.UNKNOWN
    #     )

    # if request.GET["dr_auth_status"] != "ok":
    #     return render_authentication_error(
    #         request, RapidConnectProvider.id, error=AuthError.DENIED
    #     )

    # if "dr_auth_code" not in request.GET:
    #     return render_authentication_error(
    #         request, RapidConnectProvider.id, error=AuthError.UNKNOWN
    #     )

    ret = None
    auth_exception = None
    try:
        app = providers.registry.by_id(RapidConnectProvider.id, request).get_app(request)
        audience = AUDIENCE
        if not audience:
            audience = request.scheme + "://" + request.get_host()
        token = jwt.decode(request.POST["assertion"], app.secret, audience=audience)
        attributes = token[ATTRIBUTE_KEY]
        # 'cn': 'Radomirs Cirskis',
        # 'displayname': 'Radomirs Cirskis',
        # 'surname': 'Cirskis',
        # 'givenname': 'Radomirs',
        # 'mail': 'rcir178@aucklanduni.ac.nz',
        # 'edupersonprincipalname': 'rcir178@auckland.ac.nz',
        # 'edupersonorcid': 'http://orcid.org/0000-0002-7902-638X',
        # 'edupersonscopedaffiliation': '',

        provider = providers.registry.by_id(RapidConnectProvider.id, request)
        login = provider.sociallogin_from_response(request, attributes)
        login.token = SocialToken(app=app, token=token["jti"])

        # login.state = SocialLogin.unstash_state(request)

        ret = complete_social_login(request, login)
    except (requests.RequestException, RapidConnectApiError) as e:
        auth_exception = e

    if not ret:
        ret = render_authentication_error(
            request, RapidConnectProvider.id, exception=auth_exception
        )

    return ret
