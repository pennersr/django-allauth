from django.contrib import messages
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from allauth.utils import generate_unique_username, email_address_exists
from allauth.account.utils import send_email_confirmation, \
    perform_login, complete_signup
from allauth.account import app_settings as account_settings

from models import SocialLogin
import app_settings
import signals

def _process_signup(request, sociallogin):
    # If email is specified, check for duplicate and if so, no auto signup.
    auto_signup = app_settings.AUTO_SIGNUP
    email = sociallogin.account.user.email
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
        elif account_settings.EMAIL_REQUIRED:
            # Nope, email is required and we don't have it yet...
            auto_signup = False
    if not auto_signup:
        request.session['socialaccount_sociallogin'] = sociallogin
        url = reverse('socialaccount_signup')
        ret = HttpResponseRedirect(url)
    else:
        # FIXME: There is some duplication of logic inhere
        # (create user, send email, in active etc..)
        u = sociallogin.account.user
        u.username = generate_unique_username(u.username
                                              or email 
                                              or 'user')
        u.last_name = (u.last_name or '') \
            [0:User._meta.get_field('last_name').max_length]
        u.first_name = (u.first_name or '') \
            [0:User._meta.get_field('first_name').max_length]
        u.email = email or ''
        u.set_unusable_password()
        sociallogin.save()
        send_email_confirmation(u, request=request)
        ret = complete_social_signup(request, sociallogin)
    return ret


def _login_social_account(request, sociallogin):
    user = sociallogin.account.user
    if not user.is_active:
        ret = render_to_response(
            'socialaccount/account_inactive.html',
            {},
            context_instance=RequestContext(request))
    else:
        ret = perform_login(request, user, 
                            redirect_url=sociallogin.get_redirect_url())
    return ret


def render_authentication_error(request, extra_context={}):
    return render_to_response(
        "socialaccount/authentication_error.html",
        extra_context, context_instance=RequestContext(request))


def complete_social_login(request, sociallogin):
    assert not sociallogin.is_existing
    sociallogin.lookup()
    signals.pre_social_login.send(sender=SocialLogin,
                                  request=request, 
                                  sociallogin=sociallogin)
    if request.user.is_authenticated():
        if sociallogin.is_existing:
            # Existing social account, existing user
            if sociallogin.account.user != request.user:
                # Social account of other user. Simply logging in may
                # not be correct in the case that the user was
                # attempting to hook up another social account to his
                # existing user account. For now, this scenario is not
                # supported. Issue is that one cannot simply remove
                # the social account from the other user, as that may
                # render the account unusable.
                pass
            ret = _login_social_account(request, sociallogin)
        else:
            # New social account
            sociallogin.account.user = request.user
            sociallogin.save()
            default_next = reverse('socialaccount_connections')
            next = sociallogin.get_redirect_url(fallback=default_next)
            messages.add_message(request, messages.INFO, 
                                 _('The social account has been connected'
                                   ' to your existing account'))
            return HttpResponseRedirect(next)
    else:
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
                           sociallogin.get_redirect_url())


# TODO: Factor out callable importing functionality
# See: account.utils.user_display
def import_path(path):
    modname, _, attr = path.rpartition('.')
    m = __import__(modname, fromlist=[attr])
    return getattr(m, attr)
