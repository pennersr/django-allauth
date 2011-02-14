from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout as auth_logout
from django.utils.translation import ugettext, ugettext_lazy as _

from allauth.utils import get_login_redirect_url, \
    generate_unique_username, get_email_address
from allauth.account.utils import send_email_confirmation, \
    perform_login, complete_signup
from allauth.account import app_settings as account_settings

import app_settings

def _process_signup(request, data, account):
    # If email is specified, check for duplicate and if so, no auto signup.
    auto_signup = app_settings.AUTO_SIGNUP
    email = data.get('email')
    if auto_signup:
        # Let's check if auto_signup is really possible...
        if email:
            if account_settings.UNIQUE_EMAIL:
                email_address = get_email_address(email)
                if email_address:
                    # Oops, another user already has this address.  We
                    # cannot simply connect this social account to the
                    # existing user. Reason is that the email adress may
                    # not be verified, meaning, the user may be a hacker
                    # that has added your email address to his account in
                    # the hope that you fall in his trap.  We cannot check
                    # on 'email_address.verified' either, because
                    # 'email_address' is not guaranteed to be verified.
                    auto_signup = False
                    # FIXME: We redirect to signup form -- user will
                    # see email address conflict only after posting
                    # whereas we detected it here already.
        elif account_settings.EMAIL_REQUIRED:
            # Nope, email is required and we don't have it yet...
            auto_signup = False
    if not auto_signup:
        request.session['socialaccount_signup'] = dict(data=data,
                                                       account=account)
        ret = HttpResponseRedirect(reverse('socialaccount_signup'))
    else:
        # FIXME: There is some duplication of logic inhere 
        # (create user, send email, in active etc..)
        username = generate_unique_username \
            (data.get('username', email or 'user'))
        u = User(username=username,
                 email=email or '',
                 last_name = data.get('last_name', ''),
                 first_name = data.get('first_name', ''))
        u.set_unusable_password()
        u.is_active = not account_settings.EMAIL_VERIFICATION
        u.save()
        account.user = u
        account.save()
        send_email_confirmation(u, request=request)
        ret = complete_social_signup(request, u, account)
    return ret
        


def _login_social_account(request, account):
    user = account.user
    perform_login(request, user)
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
            ret = _process_signup(request, data, account)
    return ret


def _copy_avatar(request, user, account):
    import urllib2
    from django.core.files.base import ContentFile
    from urlparse import urlparse
    from avatar.models import Avatar
    url = account.get_avatar_url()    
    if url:
        ava = Avatar(user=user)
        ava.primary = Avatar.objects.filter(user=user).count() == 0
        try:
            name = urlparse(url).path
            content = urllib2.urlopen(url).read()
            ava.avatar.save(name, ContentFile(content))
        except IOError, e:
            # Let's nog make a big deal out of this...
            pass


def complete_social_signup(request, user, account):
    success_url = get_login_redirect_url(request)
    if app_settings.AVATAR_SUPPORT:
        _copy_avatar(request, user, account)
    return complete_signup(request, user, success_url)
