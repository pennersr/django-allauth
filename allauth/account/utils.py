import hashlib
import random

from datetime import timedelta
try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now

from django.contrib import messages
from django.shortcuts import render
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import login
from django.utils.translation import ugettext_lazy as _, ugettext
from django.http import HttpResponseRedirect

from allauth.utils import import_callable

import signals

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



_user_display_callable = None

def user_display(user):
    global _user_display_callable
    if not _user_display_callable:
        f = getattr(settings, "ACCOUNT_USER_DISPLAY",
                    lambda user: user.username)
        _user_display_callable = import_callable(f)
    return _user_display_callable(user)


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
    from models import EmailAddress

    # not is_active: social users are redirected to a template
    # local users are stopped due to form validation checking is_active
    assert user.is_active
    if (app_settings.EMAIL_VERIFICATION
        and not EmailAddress.objects.filter(user=user,
                                            verified=True).exists()):
        send_email_confirmation(user, request=request)
        return render(request,
                      "account/verification_sent.html",
                      { "email": user.email })
    # HACK: This may not be nice. The proper Django way is to use an
    # authentication backend, but I fail to see any added benefit
    # whereas I do see the downsides (having to bother the integrator
    # to set up authentication backends in settings.py
    if not hasattr(user, 'backend'):
        user.backend = "django.contrib.auth.backends.ModelBackend"
    signals.user_logged_in.send(sender=user.__class__, 
                                request=request, 
                                user=user)
    login(request, user)
    messages.add_message(request, messages.SUCCESS,
                         ugettext("Successfully signed in as %(user)s.") % { "user": user_display(user) } )

    if not redirect_url:
        redirect_url = get_default_redirect(request)
    return HttpResponseRedirect(redirect_url)


def complete_signup(request, user, success_url):
    signals.user_signed_up.send(sender=user.__class__, 
                                request=request, 
                                user=user)
    return perform_login(request, user, redirect_url=success_url)


def send_email_confirmation(user, request=None):
    """
    E-mail verification mails are sent:
    a) Explicitly: when a user signs up
    b) Implicitly: when a user attempts to log in using an unverified
    e-mail while EMAIL_VERIFICATION is mandatory.

    Especially in case of b), we want to limit the number of mails
    sent (consider a user retrying a few times), which is why there is
    a cooldown period before sending a new mail.
    """
    from models import EmailAddress, EmailConfirmation

    COOLDOWN_PERIOD = timedelta(minutes=3)
    email = user.email
    if email:
        try:
            email_address = EmailAddress.objects.get(user=user,
                                                     email__iexact=email)
            email_confirmation_sent = EmailConfirmation.objects \
                .filter(sent__gt=now() - COOLDOWN_PERIOD,
                        email_address=email_address) \
                .exists()
            if not email_confirmation_sent:
                email_address.send_confirmation()
        except EmailAddress.DoesNotExist:
            email_address = EmailAddress.objects.add_email(user, user.email, confirm=True)
            assert email_address
            email_confirmation_sent = False
        if request and not email_confirmation_sent:
            messages.info(request,
                _(u"Confirmation e-mail sent to %(email)s") % {"email": email}
            )

def format_email_subject(subject):
    prefix = app_settings.EMAIL_SUBJECT_PREFIX
    if prefix is None:
        site = Site.objects.get_current()
        prefix = "[{name}] ".format(name=site.name)
    return prefix + unicode(subject)


def sync_user_email_addresses(user):
    """
    Keep user.email in sync with user.emailadress_set.

    Under some circumstances the user.email may not have ended up as
    an EmailAddress record, e.g. in the case of manually created admin
    users.
    """
    from models import EmailAddress
    if user.email and not EmailAddress.objects.filter(user=user,
                                                      email=user.email).exists():
        if app_settings.UNIQUE_EMAIL and EmailAddress.objects.filter(email=user.email).exists():
            # Bail out
            return
        EmailAddress.objects.create(user=user,
                                    email=user.email,
                                    primary=False,
                                    verified=False)


def random_token(extra=None, hash_func=hashlib.sha256):
    if extra is None:
        extra = []
    bits = extra + [str(random.SystemRandom().getrandbits(512))]
    return hash_func("".join(bits)).hexdigest()
