from django.contrib import messages
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import login
from django.utils.translation import ugettext_lazy as _, ugettext
from django.http import HttpResponseRedirect

from emailconfirmation.models import EmailAddress

from signals import user_logged_in

import app_settings


LOGIN_REDIRECT_URLNAME = getattr(settings, "LOGIN_REDIRECT_URLNAME", "")


def get_default_redirect(request, redirect_field_name="next",
        login_redirect_urlname=LOGIN_REDIRECT_URLNAME, session_key_value="redirect_to"):
    """
    Returns the URL to be used in login procedures by looking at different
    values in the following order:
    
    - a REQUEST value, GET or POST, named "next" by default.
    - LOGIN_REDIRECT_URL - the URL in the setting
    - LOGIN_REDIRECT_URLNAME - the name of a URLconf entry in the settings
    """
    if login_redirect_urlname:
        default_redirect_to = reverse(login_redirect_urlname)
    else:
        default_redirect_to = settings.LOGIN_REDIRECT_URL
    redirect_to = request.REQUEST.get(redirect_field_name)
    if not redirect_to:
        # try the session if available
        if hasattr(request, "session"):
            redirect_to = request.session.get(session_key_value)
    # light security check -- make sure redirect_to isn't garabage.
    if not redirect_to or "://" in redirect_to or " " in redirect_to:
        redirect_to = default_redirect_to
    return redirect_to


def user_display(user):
    func = getattr(settings, "ACCOUNT_USER_DISPLAY", lambda user: user.username)
    return func(user)


# def has_openid(request):
#     """
#     Given a HttpRequest determine whether the OpenID on it is associated thus
#     allowing caller to know whether OpenID is good to depend on.
#     """
#     from django_openid.models import UserOpenidAssociation
#     for association in UserOpenidAssociation.objects.filter(user=request.user):
#         if association.openid == unicode(request.openid):
#             return True
#     return False


def perform_login(request, user, redirect_url=None):
    # not is_active: social users are redirected to a template
    # local users are stopped due to form validation checking is_active
    assert user.is_active
    if (app_settings.EMAIL_VERIFICATION
        and not EmailAddress.objects.filter(user=user,
                                            verified=True).exists()):
        # TODO: Resend another verification mail
        return render(request, 
                      "account/verification_sent.html",
                      { "email": user.email })
    # HACK: This may not be nice. The proper Django way is to use an
    # authentication backend, but I fail to see any added benefit
    # whereas I do see the downsides (having to bother the integrator
    # to set up authentication backends in settings.py
    if not hasattr(user, 'backend'):
        user.backend = "django.contrib.auth.backends.ModelBackend"
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    login(request, user)
    messages.add_message(request, messages.SUCCESS,
                         ugettext("Successfully signed in as %(user)s.") % { "user": user_display(user) } )
            
    if not redirect_url:
        redirect_url = get_default_redirect(request)
    return HttpResponseRedirect(redirect_url)


def complete_signup(request, user, success_url):
    return perform_login(request, user, redirect_url=success_url)


def send_email_confirmation(user, request=None):
    email = user.email
    if email:
        if EmailAddress.objects.add_email(user, user.email) and request:
            messages.info(request,
                _(u"Confirmation e-mail sent to %(email)s") % {"email": email}
            )

def format_email_subject(subject):
    prefix = app_settings.EMAIL_SUBJECT_PREFIX
    if prefix is None:
        site = Site.objects.get_current()
        prefix = "[{name}] ".format(name=site.name)
    return prefix + unicode(subject)
