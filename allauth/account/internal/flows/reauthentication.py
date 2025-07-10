import time
from typing import Dict, List, Optional

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode

from allauth import app_settings as allauth_settings
from allauth.account import app_settings
from allauth.account.authentication import get_authentication_records
from allauth.account.internal.flows.login import record_authentication
from allauth.core.exceptions import ReauthenticationRequired
from allauth.core.internal.httpkit import deserialize_request, serialize_request
from allauth.core.internal.urlkit import script_aware_resolve
from allauth.utils import import_callable


STATE_SESSION_KEY = "account_reauthentication_state"


def reauthenticate_by_password(request: HttpRequest) -> None:
    record_authentication(
        request, request.user, method="password", reauthenticated=True
    )


def stash_and_reauthenticate(
    request: HttpRequest, state: dict, callback: str
) -> HttpResponseRedirect:
    request.session[STATE_SESSION_KEY] = {
        "state": state,
        "callback": callback,
    }
    return HttpResponseRedirect(reverse("account_reauthenticate"))


def suspend_request(request: HttpRequest, redirect_to: str) -> HttpResponseRedirect:
    path = request.get_full_path()
    if request.method == "POST":
        request.session[STATE_SESSION_KEY] = {"request": serialize_request(request)}
    return HttpResponseRedirect(
        redirect_to + "?" + urlencode({REDIRECT_FIELD_NAME: path})
    )


def resume_request(request: HttpRequest) -> Optional[HttpResponseRedirect]:
    from allauth.account.utils import get_next_redirect_url

    state = request.session.pop(STATE_SESSION_KEY, None)
    if state and "callback" in state:
        callback = import_callable(state["callback"])
        return callback(request, state["state"])

    url = get_next_redirect_url(request, REDIRECT_FIELD_NAME)
    if not url:
        return None
    if state and "request" in state:
        suspended_request = deserialize_request(state["request"], request)
        if suspended_request.path == url:
            resolved = script_aware_resolve(suspended_request.path)
            return resolved.func(suspended_request, *resolved.args, **resolved.kwargs)
    return HttpResponseRedirect(url)


def raise_if_reauthentication_required(request: HttpRequest) -> None:
    if not did_recently_authenticate(request):
        raise ReauthenticationRequired()


def did_recently_authenticate(request: HttpRequest) -> bool:
    if request.user.is_anonymous:
        return False
    if not get_reauthentication_flows(request.user):
        # TODO: This user only has social accounts attached. Now, ideally, you
        # would want to reauthenticate over at the social account provider. For
        # now, this is not implemented. Although definitely suboptimal, this
        # method is currently used for reauthentication checks over at MFA, and,
        # users that delegate the security of their account to an external
        # provider like Google typically use MFA over there anyway.
        return True
    methods = get_authentication_records(request)
    if not methods:
        return False
    authenticated_at = methods[-1]["at"]
    return time.time() - authenticated_at < app_settings.REAUTHENTICATION_TIMEOUT


def get_reauthentication_flows(user) -> List[Dict]:
    ret: List[Dict] = []
    if not user.is_authenticated:
        return ret
    if user.has_usable_password():
        entry = {
            "id": "reauthenticate",
        }
        ret.append(entry)
    if allauth_settings.MFA_ENABLED:
        from allauth.mfa.models import Authenticator
        from allauth.mfa.utils import is_mfa_enabled

        types = []
        for typ in Authenticator.Type:
            if is_mfa_enabled(user, types=[typ]):
                types.append(typ)
        if types:
            ret.append({"id": "mfa_reauthenticate", "types": types})
    return ret
