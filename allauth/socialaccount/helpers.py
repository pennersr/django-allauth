from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout as auth_logout
from django.utils.translation import ugettext, ugettext_lazy as _
from allauth.utils import get_login_redirect_url, generate_unique_username

import app_settings

def _process_signup(request, account):
    if app_settings.SIGNUP_USERNAME \
            or app_settings.SIGNUP_EMAIL:
        request.session['socialaccount_account'] = account
        request.session['next'] = get_login_redirect_url(request)
        ret = HttpResponseRedirect(reverse('socialaccount_signup'))
    else:
        u = User()
        u.set_unusable_password()
        u.username = generate_unique_username(account.suggest_username())
        u.save()
        account.user = u
        account.save()
        ret = _login_social_account(request, account)
    return ret
        


def _login_social_account(request, account):
    user = account.authenticate()
    assert user
    login(request, user)
    if not user.is_active:
        ret = render_to_response(
            'socialaccount/account_inactive.html',
            {},
            context_instance=RequestContext(request))
    else:
        ret = HttpResponseRedirect(get_login_redirect_url(request))
    return ret


def render_authentication_error(request, extra_context={}):
    return render_to_response(
        "socialaccount/authentication_error.html", 
        extra_context, context_instance=RequestContext(request))


def complete_social_login(request, data, account):
    if request.user.is_authenticated():
        if account.pk:
            # Existing social account, existing user
            if account.user != request.user:
                # Social account of other user. Simply logging in may
                # not be correct in the case that the user was
                # attempting to hook up another social account to his
                # existing user account. For now, this scenario is not
                # supported. Issue is that one cannot simply remove
                # the social account from the other user, as that may
                # render the account unusable.
                pass
            ret = _login_social_account(request, account)
        else:
            # New social account
            account.user = request.user
            account.save()
            messages.add_message \
            (request, messages.INFO, 
             _('The social account has been connected to your existing account'))
            return HttpResponseRedirect(reverse('socialaccount_connections'))
    else:
        if account.pk:
            # Login existing user
            ret = _login_social_account(request, account)
        else:
            # New social user
            ret = _process_signup(request, account)
    return ret



