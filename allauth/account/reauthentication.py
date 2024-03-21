import time

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.urls import resolve, reverse
from django.utils.http import urlencode

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.authentication import get_authentication_records
from allauth.core.exceptions import ReauthenticationRequired
from allauth.core.internal.httpkit import (
    deserialize_request,
    serialize_request,
)
from allauth.utils import import_callable


STATE_SESSION_KEY = "account_reauthentication_state"


def suspend_request(request, redirect_to):
    path = request.get_full_path()
    if request.method == "POST":
        request.session[STATE_SESSION_KEY] = {"request": serialize_request(request)}
    return HttpResponseRedirect(
        redirect_to + "?" + urlencode({REDIRECT_FIELD_NAME: path})
    )


def resume_request(request):
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
            resolved = resolve(suspended_request.path)
            return resolved.func(suspended_request, *resolved.args, **resolved.kwargs)
    return HttpResponseRedirect(url)


def reauthenticate_then_callback(request, serialize_state, callback):
    # TODO: Currently, ACCOUNT_REAUTHENTICATION_REQUIRED does not play well with
    # XHR.
    if did_recently_authenticate(request):
        return None
    request.session[STATE_SESSION_KEY] = {
        "state": serialize_state(request),
        "callback": callback,
    }
    return HttpResponseRedirect(reverse("account_reauthenticate"))


def raise_if_reauthentication_required(request):
    if not did_recently_authenticate(request):
        raise ReauthenticationRequired()


def did_recently_authenticate(request):
    if request.user.is_anonymous:
        return False
    if not get_adapter().get_reauthentication_methods(request.user):
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
