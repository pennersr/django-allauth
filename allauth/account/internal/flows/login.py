from django.urls import reverse

from allauth.account.adapter import get_adapter
from allauth.account.authentication import record_authentication
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.utils import build_absolute_uri


def _get_login_hook_kwargs(login):
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


def perform_password_login(request, credentials, login):
    extra_data = {
        field: credentials.get(field)
        for field in ["email", "username"]
        if credentials.get(field)
    }
    record_authentication(request, method="password", **extra_data)
    return perform_login(request, login)


def perform_login(request, login):
    adapter = get_adapter()
    hook_kwargs = _get_login_hook_kwargs(login)
    response = adapter.pre_login(request, login.user, **hook_kwargs)
    if response:
        return response
    return resume_login(request, login)


def resume_login(request, login):
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


def send_unknown_account_email(request, email):
    signup_url = build_absolute_uri(request, reverse("account_signup"))
    context = {
        "request": request,
        "signup_url": signup_url,
    }
    get_adapter().send_mail("account/email/unknown_account", email, context)
