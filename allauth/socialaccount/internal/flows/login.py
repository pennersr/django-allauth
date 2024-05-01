from django.http import HttpResponseRedirect

from allauth.account import authentication
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.utils import perform_login
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount import app_settings, signals
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.internal.flows.connect import connect
from allauth.socialaccount.internal.flows.signup import (
    clear_pending_signup,
    process_signup,
)
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.base import AuthProcess


def _login(request, sociallogin):
    sociallogin._accept_login()
    record_authentication(request, sociallogin)
    return perform_login(
        request,
        sociallogin.user,
        email_verification=app_settings.EMAIL_VERIFICATION,
        redirect_url=sociallogin.get_redirect_url(request),
        signal_kwargs={"sociallogin": sociallogin},
    )


def complete_login(request, sociallogin):
    clear_pending_signup(request)
    assert not sociallogin.is_existing
    sociallogin.lookup()
    try:
        get_adapter().pre_social_login(request, sociallogin)
        signals.pre_social_login.send(
            sender=SocialLogin, request=request, sociallogin=sociallogin
        )
        process = sociallogin.state.get("process")
        if process == AuthProcess.REDIRECT:
            return _redirect(request, sociallogin)
        elif process == AuthProcess.CONNECT:
            return connect(request, sociallogin)
        else:
            return _authenticate(request, sociallogin)
    except ImmediateHttpResponse as e:
        return e.response


def _redirect(request, sociallogin):
    next_url = sociallogin.get_redirect_url(request) or "/"
    return HttpResponseRedirect(next_url)


def _authenticate(request, sociallogin):
    if request.user.is_authenticated:
        get_account_adapter(request).logout(request)
    if sociallogin.is_existing:
        # Login existing user
        ret = _login(request, sociallogin)
    else:
        # New social user
        ret = process_signup(request, sociallogin)
    return ret


def record_authentication(request, sociallogin):
    authentication.record_authentication(
        request,
        "socialaccount",
        **{
            "provider": sociallogin.account.provider,
            "uid": sociallogin.account.uid,
        }
    )
