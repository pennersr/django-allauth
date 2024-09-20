import time
from typing import Any, Dict

from django.http import HttpRequest, HttpResponse

from allauth.account.adapter import get_adapter
from allauth.account.models import Login
from allauth.core.exceptions import ImmediateHttpResponse


AUTHENTICATION_METHODS_SESSION_KEY = "account_authentication_methods"


def record_authentication(request, method, **extra_data):
    """Here we keep a log of all authentication methods used within the current
    session.  Important to note is that having entries here does not imply that
    a user is fully signed in. For example, consider a case where a user
    authenticates using a password, but fails to complete the 2FA challenge.
    Or, a user successfully signs in into an inactive account or one that still
    needs verification. In such cases, ``request.user`` is still anonymous, yet,
    we do have an entry here.

    Example data::

        {'method': 'password',
         'at': 1701423602.7184925,
         'username': 'john.doe'}

        {'method': 'socialaccount',
         'at': 1701423567.6368647,
         'provider': 'amazon',
         'uid': 'amzn1.account.K2LI23KL2LK2'}

        {'method': 'mfa',
         'at': 1701423602.6392953,
         'id': 1,
         'type': 'totp'}

    """
    methods = request.session.get(AUTHENTICATION_METHODS_SESSION_KEY, [])
    data = {
        "method": method,
        "at": time.time(),
        **extra_data,
    }
    methods.append(data)
    request.session[AUTHENTICATION_METHODS_SESSION_KEY] = methods


def _get_login_hook_kwargs(login: Login) -> Dict[str, Any]:
    """
    TODO: Just break backwards compatibility and pass only `login` to
    `pre/post_login()`.
    """
    return dict(
        email_verification=login.email_verification,
        redirect_url=login.redirect_url,
        signal_kwargs=login.signal_kwargs,
        signup=login.signup,
        email=login.email,
    )


def perform_password_login(
    request: HttpRequest, credentials: Dict[str, Any], login: Login
) -> HttpResponse:
    extra_data = {
        field: credentials.get(field)
        for field in ["email", "username"]
        if credentials.get(field)
    }
    record_authentication(request, method="password", **extra_data)
    return perform_login(request, login)


def perform_login(request: HttpRequest, login: Login) -> HttpResponse:
    adapter = get_adapter()
    hook_kwargs = _get_login_hook_kwargs(login)
    response = adapter.pre_login(request, login.user, **hook_kwargs)
    if response:
        return response
    return resume_login(request, login)


def resume_login(request: HttpRequest, login: Login) -> HttpResponse:
    from allauth.account.stages import LoginStageController

    adapter = get_adapter()
    ctrl = LoginStageController(request, login)
    try:
        response = ctrl.handle()
        if response:
            return response
        adapter.login(request, login.user)
        hook_kwargs = _get_login_hook_kwargs(login)
        response = adapter.post_login(request, login.user, **hook_kwargs)
        if response:
            return response
    except ImmediateHttpResponse as e:
        response = e.response
    return response
