from django.contrib import messages
from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render

from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.utils import complete_signup, perform_login, user_username
from allauth.exceptions import ImmediateHttpResponse

from . import app_settings, signals
from ..compat import is_anonymous, is_authenticated, reverse
from .adapter import get_adapter
from .models import SocialLogin
from .providers.base import AuthError, AuthProcess


def _process_signup(request, sociallogin):
    auto_signup = get_adapter(request).is_auto_signup_allowed(
        request,
        sociallogin)
    if not auto_signup:
        request.session['socialaccount_sociallogin'] = sociallogin.serialize()
        url = reverse('socialaccount_signup')
        ret = HttpResponseRedirect(url)
    else:
        # Ok, auto signup it is, at least the e-mail address is ok.
        # We still need to check the username though...
        if account_settings.USER_MODEL_USERNAME_FIELD:
            username = user_username(sociallogin.user)
            try:
                get_account_adapter(request).clean_username(username)
            except ValidationError:
                # This username is no good ...
                user_username(sociallogin.user, '')
        # FIXME: This part contains a lot of duplication of logic
        # ("closed" rendering, create user, send email, in active
        # etc..)
        try:
            if not get_adapter(request).is_open_for_signup(
                    request,
                    sociallogin):
                return render(
                    request,
                    "account/signup_closed." +
                    account_settings.TEMPLATE_EXTENSION
                )
        except ImmediateHttpResponse as e:
            return e.response
        get_adapter(request).save_user(request, sociallogin, form=None)
        ret = complete_social_signup(request, sociallogin)
    return ret


def _login_social_account(request, sociallogin):
    return perform_login(request, sociallogin.user,
                         email_verification=app_settings.EMAIL_VERIFICATION,
                         redirect_url=sociallogin.get_redirect_url(request),
                         signal_kwargs={"sociallogin": sociallogin})


def render_authentication_error(request,
                                provider_id,
                                error=AuthError.UNKNOWN,
                                exception=None,
                                extra_context=None):
    try:
        if extra_context is None:
            extra_context = {}
        get_adapter(request).authentication_error(
            request,
            provider_id,
            error=error,
            exception=exception,
            extra_context=extra_context)
    except ImmediateHttpResponse as e:
        return e.response
    if error == AuthError.CANCELLED:
        return HttpResponseRedirect(reverse('socialaccount_login_cancelled'))
    context = {
        'auth_error': {
            'provider': provider_id,
            'code': error,
            'exception': exception
        }
    }
    context.update(extra_context)
    return render(
        request,
        "socialaccount/authentication_error." +
        account_settings.TEMPLATE_EXTENSION,
        context
    )


def _add_social_account(request, sociallogin):
    if is_anonymous(request.user):
        # This should not happen. Simply redirect to the connections
        # view (which has a login required)
        return HttpResponseRedirect(reverse('socialaccount_connections'))
    level = messages.INFO
    message = 'socialaccount/messages/account_connected.txt'
    action = None
    if sociallogin.is_existing:
        if sociallogin.user != request.user:
            # Social account of other user. For now, this scenario
            # is not supported. Issue is that one cannot simply
            # remove the social account from the other user, as
            # that may render the account unusable.
            level = messages.ERROR
            message = 'socialaccount/messages/account_connected_other.txt'
        else:
            # This account is already connected -- we give the opportunity
            # for customized behaviour through use of a signal. If not
            # implemented, we render the standard "account connected"
            # message without actually doing anything.
            action = 'updated'
            try:
                signals.social_account_updated.send(
                    sender=SocialLogin,
                    request=request,
                    sociallogin=sociallogin
                )
            except ImmediateHttpResponse as e:
                return e.response
    else:
        # New account, let's connect
        action = 'added'
        sociallogin.connect(request, request.user)
        try:
            signals.social_account_added.send(sender=SocialLogin,
                                              request=request,
                                              sociallogin=sociallogin)
        except ImmediateHttpResponse as e:
            return e.response
    default_next = get_adapter(request).get_connect_redirect_url(
        request,
        sociallogin.account)
    next_url = sociallogin.get_redirect_url(request) or default_next
    get_account_adapter(request).add_message(
        request, level, message,
        message_context={
            'sociallogin': sociallogin,
            'action': action
        }
    )
    return HttpResponseRedirect(next_url)


def complete_social_login(request, sociallogin):
    assert not sociallogin.is_existing
    sociallogin.lookup()
    try:
        get_adapter(request).pre_social_login(request, sociallogin)
        signals.pre_social_login.send(sender=SocialLogin,
                                      request=request,
                                      sociallogin=sociallogin)
    except ImmediateHttpResponse as e:
        return e.response
    process = sociallogin.state.get('process')
    if process == AuthProcess.REDIRECT:
        return _social_login_redirect(request, sociallogin)
    elif process == AuthProcess.CONNECT:
        return _add_social_account(request, sociallogin)
    else:
        return _complete_social_login(request, sociallogin)


def _social_login_redirect(request, sociallogin):
    next_url = sociallogin.get_redirect_url(request) or '/'
    return HttpResponseRedirect(next_url)


def _complete_social_login(request, sociallogin):
    if is_authenticated(request.user):
        get_account_adapter(request).logout(request)
    if sociallogin.is_existing:
        # Login existing user
        ret = _login_social_account(request, sociallogin)
    else:
        # New social user
        ret = _process_signup(request, sociallogin)
    return ret


def complete_social_signup(request, sociallogin):
    return complete_signup(request,
                           sociallogin.user,
                           app_settings.EMAIL_VERIFICATION,
                           sociallogin.get_redirect_url(request),
                           signal_kwargs={'sociallogin': sociallogin})


# TODO: Factor out callable importing functionality
# See: account.utils.user_display
def import_path(path):
    modname, _, attr = path.rpartition('.')
    m = __import__(modname, fromlist=[attr])
    return getattr(m, attr)
