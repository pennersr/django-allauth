from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.forms import ValidationError
from django.core.urlresolvers import reverse

from allauth.account.utils import (perform_login, complete_signup,
                                   user_username)
from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.exceptions import ImmediateHttpResponse

from .models import SocialLogin
from .models import SocialAccount
from . import app_settings
from . import signals
from .adapter import get_adapter


def _process_signup(request, sociallogin):
    auto_signup = get_adapter().is_auto_signup_allowed(request,
                                                       sociallogin)
    if not auto_signup:
        request.session['socialaccount_sociallogin'] = sociallogin.serialize()
        url = reverse('socialaccount_signup')
        ret = HttpResponseRedirect(url)
    else:
        # Ok, auto signup it is, at least the e-mail address is ok.
        # We still need to check the username though...
        if account_settings.USER_MODEL_USERNAME_FIELD:
            username = user_username(sociallogin.account.user)
            try:
                get_account_adapter().clean_username(username)
            except ValidationError:
                # This username is no good ...
                user_username(sociallogin.account.user, '')
        # FIXME: This part contains a lot of duplication of logic
        # ("closed" rendering, create user, send email, in active
        # etc..)
        try:
            if not get_adapter().is_open_for_signup(request,
                                                    sociallogin):
                return render(request,
                              "account/signup_closed.html")
        except ImmediateHttpResponse as e:
            return e.response
        get_adapter().save_user(request, sociallogin, form=None)
        ret = complete_social_signup(request, sociallogin)
    return ret


def _login_social_account(request, sociallogin):
    return perform_login(request, sociallogin.account.user,
                         email_verification=app_settings.EMAIL_VERIFICATION,
                         redirect_url=sociallogin.get_redirect_url(request),
                         signal_kwargs={"sociallogin": sociallogin})


def render_authentication_error(request, extra_context={}):
    # Providing context variable for identifying auth errors
    auth_error = extra_context.get('auth_error', 'undefined_error')
    adapter = extra_context.get('adapter', None)
    sociallogin = extra_context.get('sociallogin', None)

    # Build sociallogin  to provide more personalized error handling.
    if not sociallogin:
        if adapter:
            provider = adapter.get_provider()
            try:
                socialaccount = SocialAccount.objects.filter(user=request.user,
                                                      provider=provider.id)
                login = SocialLogin(socialaccount)
            except TypeError:
                login = SocialLogin()

            if adapter.supports_state:
                    login.state = SocialLogin \
                        .verify_and_unstash_state(
                            request,
                            request.REQUEST.get('state'))
            else:
                login.state = SocialLogin.unstash_state(request)
        else:
            login = SocialLogin()
            login.state = SocialLogin.unstash_state(request)
        sociallogin = login #or auth_error

    # provide the error for efficient error handling outside allauth.
    sociallogin.error = auth_error
    # provide the error for efficient error handling in templates.
    extra_context['sociallogin'] = sociallogin

    # Authenticated users did not necessarily get an auth_error. Perhaps
    # permissions_denied, login_canceled, or token_expired. So let's provide
    # a hook for handling flows out of allauth scope.  This is essential for
    # providing Incremental authorization as recommended by providers.
    try:
        get_adapter().social_login_error(request, sociallogin)
        signals.social_login_error.send(sender=SocialLogin,
                                      request=request,
                                      sociallogin=sociallogin)
    except ImmediateHttpResponse as e:
        return e.response

    # Provide default error handling for allauth
    next_url = sociallogin.state.get('next', None) if login else None
    non_auth_errors = ['login_canceled', 'permission_denied']
    if auth_error[0] in non_auth_errors:
        if auth_error[0] == 'login_canceled':
            level = messages.INFO
            message = 'socialaccount/messages/login_canceled.txt'
        if auth_error[0] == 'permission_denied':
            level = messages.WARNING
            message = 'socialaccount/messages/permission_denied.txt'
        if request.user.is_authenticated() and next_url:
            # authenticated users will likely want to end up where they started
            return HttpResponseRedirect(next_url)
        elif request.user.is_authenticated():
            # else authenticated users had to have come from here
            return HttpResponseRedirect(reverse('socialaccount_connections'))

        get_account_adapter().add_message(request, level, message)

        return render_to_response(
            "socialaccount/login_cancelled.html",
            extra_context, context_instance=RequestContext(request))

    return render_to_response(
        "socialaccount/authentication_error.html",
        extra_context, context_instance=RequestContext(request))


def _add_social_account(request, sociallogin):
    if request.user.is_anonymous():
        # This should not happen. Simply redirect to the connections
        # view (which has a login required)
        return HttpResponseRedirect(reverse('socialaccount_connections'))
    level = messages.INFO
    message = 'socialaccount/messages/account_connected.txt'
    if sociallogin.is_existing:
        if sociallogin.account.user != request.user:
            # Social account of other user. For now, this scenario
            # is not supported. Issue is that one cannot simply
            # remove the social account from the other user, as
            # that may render the account unusable.
            level = messages.ERROR
            message = 'socialaccount/messages/account_connected_other.txt'
        else:
            # This account is already connected -- let's play along
            # and render the standard "account connected" message
            # without actually doing anything.
            pass
    else:
        # New account, let's connect
        sociallogin.connect(request, request.user)
        try:
            signals.social_account_added.send(sender=SocialLogin,
                                              request=request,
                                              sociallogin=sociallogin)
        except ImmediateHttpResponse as e:
            return e.response
    default_next = get_adapter() \
        .get_connect_redirect_url(request,
                                  sociallogin.account)
    next_url = sociallogin.get_redirect_url(request) or default_next
    get_account_adapter().add_message(request, level, message)
    return HttpResponseRedirect(next_url)


def complete_social_login(request, sociallogin):
    assert not sociallogin.is_existing
    sociallogin.lookup()
    if sociallogin.state.get('process') == 'redirect':
        return _social_login_redirect(request, sociallogin)
    try:
        get_adapter().pre_social_login(request, sociallogin)
        signals.pre_social_login.send(sender=SocialLogin,
                                      request=request,
                                      sociallogin=sociallogin)
    except ImmediateHttpResponse as e:
        return e.response
    if sociallogin.state.get('process') == 'connect':
        return _add_social_account(request, sociallogin)
    else:
        return _complete_social_login(request, sociallogin)


def _social_login_redirect(request, sociallogin):
    # next defaults to origin path when process=redirect
    next_url = sociallogin.get_redirect_url(request)
    return HttpResponseRedirect(next_url)


def _complete_social_login(request, sociallogin):
    if request.user.is_authenticated():
        logout(request)
    if sociallogin.is_existing:
        # Login existing user
        ret = _login_social_account(request, sociallogin)
    else:
        # New social user
        ret = _process_signup(request, sociallogin)
    return ret


def complete_social_signup(request, sociallogin):
    return complete_signup(request,
                           sociallogin.account.user,
                           app_settings.EMAIL_VERIFICATION,
                           sociallogin.get_redirect_url(request),
                           signal_kwargs={'sociallogin': sociallogin})


# TODO: Factor out callable importing functionality
# See: account.utils.user_display
def import_path(path):
    modname, _, attr = path.rpartition('.')
    m = __import__(modname, fromlist=[attr])
    return getattr(m, attr)
