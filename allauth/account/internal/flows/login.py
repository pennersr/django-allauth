from typing import Any, Dict

from django.http import HttpRequest, HttpResponse

from allauth.account.adapter import get_adapter
from allauth.account.authentication import record_authentication
from allauth.account.models import Login
from allauth.core.exceptions import ImmediateHttpResponse


LOGIN_SESSION_KEY = "account_login"


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
