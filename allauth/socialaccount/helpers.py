from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.forms import ValidationError
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from allauth.utils import (generate_unique_username, email_address_exists,
                           get_user_model)
from allauth.account.utils import (perform_login, complete_signup,
                                   user_field,
                                   user_email, user_username)
from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.exceptions import ImmediateHttpResponse

from .models import SocialLogin
from . import app_settings
from . import signals
from .adapter import get_adapter

User = get_user_model()


def _process_signup(request, sociallogin):
    # If email is specified, check for duplicate and if so, no auto signup.
    auto_signup = app_settings.AUTO_SIGNUP
    email = user_email(sociallogin.account.user)
    if auto_signup:
        # Let's check if auto_signup is really possible...
        if email:
            if account_settings.UNIQUE_EMAIL:
                if email_address_exists(email):
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
        elif app_settings.EMAIL_REQUIRED:
            # Nope, email is required and we don't have it yet...
            auto_signup = False
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


def _name_from_url(url):
    """
    >>> _name_from_url('http://google.com/dir/file.ext')
    u'file.ext'
    >>> _name_from_url('http://google.com/dir/')
    u'dir'
    >>> _name_from_url('http://google.com/dir')
    u'dir'
    >>> _name_from_url('http://google.com/dir/..')
    u'dir'
    >>> _name_from_url('http://google.com/dir/../')
    u'dir'
    >>> _name_from_url('http://google.com')
    u'google.com'
    >>> _name_from_url('http://google.com/dir/subdir/file..ext')
    u'file.ext'
    """
    try:
        from urllib.parse import urlparse
    except ImportError:
        from urlparse import urlparse

    p = urlparse(url)
    for base in (p.path.split('/')[-1],
                 p.path,
                 p.netloc):
        name = ".".join(filter(lambda s: s,
                               map(slugify, base.split("."))))
        if name:
            return name


def _copy_avatar(request, user, account):
    import urllib2
    from django.core.files.base import ContentFile
    from avatar.models import Avatar
    url = account.get_avatar_url()
    if url:
        ava = Avatar(user=user)
        ava.primary = Avatar.objects.filter(user=user).count() == 0
        try:
            content = urllib2.urlopen(url).read()
            name = _name_from_url(url)
            ava.avatar.save(name, ContentFile(content))
        except IOError:
            # Let's nog make a big deal out of this...
            pass


def complete_social_signup(request, sociallogin):
    if app_settings.AVATAR_SUPPORT:
        _copy_avatar(request, sociallogin.account.user, sociallogin.account)
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
