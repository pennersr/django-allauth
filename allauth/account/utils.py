import unicodedata
from collections import OrderedDict
from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import Q
from django.utils.encoding import force_str
from django.utils.http import base36_to_int, int_to_base36

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.internal import flows
from allauth.account.models import Login
from allauth.core.internal import httpkit
from allauth.utils import (
    get_request_param,
    import_callable,
    valid_email_or_none,
)


def _unicode_ci_compare(s1, s2):
    """
    Perform case-insensitive comparison of two identifiers, using the
    recommended algorithm from Unicode Technical Report 36, section
    2.11.2(B)(2).
    """
    norm_s1 = unicodedata.normalize("NFKC", s1).casefold()
    norm_s2 = unicodedata.normalize("NFKC", s2).casefold()
    return norm_s1 == norm_s2


def get_next_redirect_url(request, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Returns the next URL to redirect to, if it was explicitly passed
    via the request.
    """
    redirect_to = get_request_param(request, redirect_field_name)
    if redirect_to and not get_adapter().is_safe_url(redirect_to):
        redirect_to = None
    return redirect_to


def get_login_redirect_url(
    request, url=None, redirect_field_name=REDIRECT_FIELD_NAME, signup=False
):
    ret = url
    if url and callable(url):
        # In order to be able to pass url getters around that depend
        # on e.g. the authenticated state.
        ret = url()
    if not ret:
        ret = get_next_redirect_url(request, redirect_field_name=redirect_field_name)
    if not ret:
        if signup:
            ret = get_adapter().get_signup_redirect_url(request)
        else:
            ret = get_adapter().get_login_redirect_url(request)
    return ret


_user_display_callable = None


def default_user_display(user):
    if app_settings.USER_MODEL_USERNAME_FIELD:
        return getattr(user, app_settings.USER_MODEL_USERNAME_FIELD)
    else:
        return force_str(user)


def user_display(user):
    global _user_display_callable
    if not _user_display_callable:
        f = getattr(settings, "ACCOUNT_USER_DISPLAY", default_user_display)
        _user_display_callable = import_callable(f)
    return _user_display_callable(user)


def user_field(user, field, *args, commit=False):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if not field:
        return
    User = get_user_model()
    try:
        field_meta = User._meta.get_field(field)
        max_length = field_meta.max_length
    except FieldDoesNotExist:
        if not hasattr(user, field):
            return
        max_length = None
    if args:
        # Setter
        v = args[0]
        if v:
            v = v[0:max_length]
        setattr(user, field, v)
        if commit:
            user.save(update_fields=[field])
    else:
        # Getter
        return getattr(user, field)


def user_username(user, *args, commit=False):
    if args and not app_settings.PRESERVE_USERNAME_CASING and args[0]:
        args = [args[0].lower()]
    return user_field(user, app_settings.USER_MODEL_USERNAME_FIELD, *args)


def user_email(user, *args, commit=False):
    if args and args[0]:
        args = [args[0].lower()]
    ret = user_field(user, app_settings.USER_MODEL_EMAIL_FIELD, *args, commit=commit)
    if ret:
        ret = ret.lower()
    return ret


def has_verified_email(user, email=None):
    from .models import EmailAddress

    emailaddress = None
    if email:
        ret = False
        try:
            emailaddress = EmailAddress.objects.get_for_user(user, email)
            ret = emailaddress.verified
        except EmailAddress.DoesNotExist:
            pass
    else:
        ret = EmailAddress.objects.filter(user=user, verified=True).exists()
    return ret


def perform_login(
    request,
    user,
    email_verification=None,
    redirect_url=None,
    signal_kwargs=None,
    signup=False,
    email=None,
):
    login = Login(
        user=user,
        email_verification=email_verification,
        redirect_url=redirect_url,
        signal_kwargs=signal_kwargs,
        signup=signup,
        email=email,
    )
    return flows.login.perform_login(request, login)


def resume_login(request, login):
    return flows.login.resume_login(request, login)


def unstash_login(request, peek=False):
    login = None
    if peek:
        data = request.session.get(flows.login.LOGIN_SESSION_KEY)
    else:
        data = request.session.pop(flows.login.LOGIN_SESSION_KEY, None)
    if isinstance(data, dict):
        try:
            login = Login.deserialize(data)
            request._account_login_accessed = True
        except ValueError:
            pass
    return login


def stash_login(request, login):
    request.session[flows.login.LOGIN_SESSION_KEY] = login.serialize()
    request._account_login_accessed = True


def complete_signup(request, user, email_verification, success_url, signal_kwargs=None):
    if signal_kwargs is None:
        signal_kwargs = {}
    signals.user_signed_up.send(
        sender=user.__class__, request=request, user=user, **signal_kwargs
    )
    return perform_login(
        request,
        user,
        email_verification=email_verification,
        signup=True,
        redirect_url=success_url,
        signal_kwargs=signal_kwargs,
    )


def cleanup_email_addresses(request, addresses):
    """
    Takes a list of EmailAddress instances and cleans it up, making
    sure only valid ones remain, without multiple primaries etc.

    Order is important: e.g. if multiple primary email addresses
    exist, the first one encountered will be kept as primary.
    """
    from .models import EmailAddress

    adapter = get_adapter()
    # Let's group by `email`
    e2a = OrderedDict()  # maps email to EmailAddress
    primary_addresses = []
    verified_addresses = []
    primary_verified_addresses = []
    for address in addresses:
        # Pick up only valid ones...
        email = valid_email_or_none(address.email)
        if not email:
            continue
        address.email = email  # `valid_email_or_none` lower cases
        # ... and non-conflicting ones...
        if (
            app_settings.UNIQUE_EMAIL
            and app_settings.PREVENT_ENUMERATION != "strict"
            and EmailAddress.objects.lookup([email])
        ):
            # Email address already exists.
            continue
        if (
            app_settings.UNIQUE_EMAIL
            and app_settings.PREVENT_ENUMERATION == "strict"
            and address.verified
            and EmailAddress.objects.is_verified(email)
        ):
            # Email address already exists, and is verified as well.
            continue
        a = e2a.get(email)
        if a:
            a.primary = a.primary or address.primary
            a.verified = a.verified or address.verified
        else:
            a = address
            a.verified = a.verified or adapter.is_email_verified(request, a.email)
            e2a[email] = a
        if a.primary:
            primary_addresses.append(a)
            if a.verified:
                primary_verified_addresses.append(a)
        if a.verified:
            verified_addresses.append(a)
    # Now that we got things sorted out, let's assign a primary
    if primary_verified_addresses:
        primary_address = primary_verified_addresses[0]
    elif verified_addresses:
        # Pick any verified as primary
        primary_address = verified_addresses[0]
    elif primary_addresses:
        # Okay, let's pick primary then, even if unverified
        primary_address = primary_addresses[0]
    elif e2a:
        # Pick the first
        primary_address = list(e2a.values())[0]
    else:
        # Empty
        primary_address = None
    # There can only be one primary
    for a in e2a.values():
        a.primary = primary_address.email.lower() == a.email.lower()
    return list(e2a.values()), primary_address


def setup_user_email(request, user, addresses):
    """
    Creates proper EmailAddress for the user that was just signed
    up. Only sets up, doesn't do any other handling such as sending
    out email confirmation mails etc.
    """
    from .models import EmailAddress

    assert not EmailAddress.objects.filter(user=user).exists()
    priority_addresses = []
    # Is there a stashed email?
    adapter = get_adapter()
    stashed_email = adapter.unstash_verified_email(request)
    if stashed_email:
        priority_addresses.append(
            EmailAddress(
                user=user, email=stashed_email.lower(), primary=True, verified=True
            )
        )
    email = user_email(user)
    if email:
        priority_addresses.append(
            EmailAddress(user=user, email=email.lower(), primary=True, verified=False)
        )
    addresses, primary = cleanup_email_addresses(
        request, priority_addresses + addresses
    )
    for a in addresses:
        a.user = user
        a.save()
    EmailAddress.objects.fill_cache_for_user(user, addresses)
    if primary and (email or "").lower() != primary.email.lower():
        user_email(user, primary.email)
        user.save()
    return primary


def send_email_confirmation(request, user, signup=False, email=None):
    """
    Email verification mails are sent:
    a) Explicitly: when a user signs up
    b) Implicitly: when a user attempts to log in using an unverified
    email while EMAIL_VERIFICATION is mandatory.

    Especially in case of b), we want to limit the number of mails
    sent (consider a user retrying a few times), which is why there is
    a cooldown period before sending a new mail. This cooldown period
    can be configured in ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN setting.

    TODO: This code is doing way too much. Looking up EmailAddress, creating
    if not present, etc. To be refactored.
    """
    from .models import EmailAddress

    adapter = get_adapter()
    sent = False
    email_address = None
    if not email:
        email = user_email(user)
    if not email:
        email_address = (
            EmailAddress.objects.filter(user=user).order_by("verified", "pk").first()
        )
        if email_address:
            email = email_address.email

    if email:
        if email_address is None:
            try:
                email_address = EmailAddress.objects.get_for_user(user, email)
            except EmailAddress.DoesNotExist:
                pass
        if email_address is not None:
            if not email_address.verified:
                send_email = adapter.should_send_confirmation_mail(
                    request, email_address, signup
                )
                if send_email:
                    email_address.send_confirmation(request, signup=signup)
                    sent = True
            else:
                send_email = False
        else:
            send_email = True
            email_address = EmailAddress.objects.add_email(
                request, user, email, signup=signup, confirm=True
            )
            sent = True
            assert email_address
        # At this point, if we were supposed to send an email we have sent it.
        if send_email:
            adapter.add_message(
                request,
                messages.INFO,
                "account/messages/email_confirmation_sent.txt",
                {"email": email, "login": not signup, "signup": signup},
            )
    if signup:
        adapter.stash_user(request, user_pk_to_url_str(user))
    return sent


def sync_user_email_addresses(user):
    """
    Keep user.email in sync with user.emailaddress_set.

    Under some circumstances the user.email may not have ended up as
    an EmailAddress record, e.g. in the case of manually created admin
    users.
    """
    from .models import EmailAddress

    email = user_email(user)
    if email and not EmailAddress.objects.filter(user=user, email=email).exists():
        # get_or_create() to gracefully handle races
        EmailAddress.objects.get_or_create(
            user=user, email=email, defaults={"primary": False, "verified": False}
        )


def filter_users_by_username(*username):
    if app_settings.PRESERVE_USERNAME_CASING:
        qlist = [
            Q(**{app_settings.USER_MODEL_USERNAME_FIELD + "__iexact": u})
            for u in username
        ]
        q = qlist[0]
        for q2 in qlist[1:]:
            q = q | q2
        ret = get_user_model()._default_manager.filter(q)
    else:
        ret = get_user_model()._default_manager.filter(
            **{
                app_settings.USER_MODEL_USERNAME_FIELD
                + "__in": [u.lower() for u in username]
            }
        )
    return ret


def filter_users_by_email(email, is_active=None, prefer_verified=False):
    """Return list of users by email address

    Typically one, at most just a few in length.  First we look through
    EmailAddress table, than customisable User model table. Add results
    together avoiding SQL joins and deduplicate.

    `prefer_verified`: When looking up users by email, there can be cases where
    users with verified email addresses are preferable above users who did not
    verify their email address. The password reset is such a use case -- if
    there is a user with a verified email than that user should be returned, not
    one of the other users.
    """
    from .models import EmailAddress

    User = get_user_model()
    email = email.lower()
    mails = EmailAddress.objects.filter(email=email).select_related("user")
    mails = list(mails)
    is_verified = False
    if prefer_verified:
        verified_mails = list(filter(lambda e: e.verified, mails))
        if verified_mails:
            mails = verified_mails
            is_verified = True
    users = []
    for e in mails:
        if _unicode_ci_compare(e.email, email):
            users.append(e.user)
    if app_settings.USER_MODEL_EMAIL_FIELD and not is_verified:
        q_dict = {app_settings.USER_MODEL_EMAIL_FIELD: email}
        user_qs = User.objects.filter(**q_dict)
        for user in user_qs.iterator():
            user_email = getattr(user, app_settings.USER_MODEL_EMAIL_FIELD)
            if _unicode_ci_compare(user_email, email):
                users.append(user)
    if is_active is not None:
        users = [u for u in set(users) if u.is_active == is_active]
    return list(set(users))


def passthrough_next_redirect_url(request, url, redirect_field_name):
    next_url = get_next_redirect_url(request, redirect_field_name)
    if next_url:
        url = httpkit.add_query_params(url, {redirect_field_name: next_url})
    return url


def user_pk_to_url_str(user):
    """
    This should return a string.
    """
    User = get_user_model()
    pk_field_class = type(User._meta.pk)
    if issubclass(pk_field_class, models.UUIDField):
        if isinstance(user.pk, str):
            return user.pk
        return user.pk.hex
    elif issubclass(pk_field_class, models.IntegerField):
        return int_to_base36(int(user.pk))
    return str(user.pk)


def url_str_to_user_pk(pk_str):
    User = get_user_model()
    remote_field = getattr(User._meta.pk, "remote_field", None)
    if remote_field and getattr(remote_field, "to", None):
        pk_field = User._meta.pk.remote_field.to._meta.pk
    else:
        pk_field = User._meta.pk
    pk_field_class = type(pk_field)
    if issubclass(pk_field_class, models.IntegerField):
        pk = base36_to_int(pk_str)
        # always call to_python() -- because there are fields like HashidField
        # that derive from IntegerField.
        pk = pk_field.to_python(pk)
    else:
        pk = pk_field.to_python(pk_str)
    return pk


def assess_unique_email(email) -> Optional[bool]:
    """
    True -- email is unique
    False -- email is already in use
    None -- email is in use, but we should hide that using email verification.
    """
    if not filter_users_by_email(email):
        # All good.
        return True
    elif not app_settings.PREVENT_ENUMERATION:
        # Fail right away.
        return False
    elif (
        app_settings.EMAIL_VERIFICATION
        == app_settings.EmailVerificationMethod.MANDATORY
    ):
        # In case of mandatory verification and enumeration prevention,
        # we can avoid creating a new account with the same (unverified)
        # email address, because we are going to send an email anyway.
        assert app_settings.PREVENT_ENUMERATION
        return None
    elif app_settings.PREVENT_ENUMERATION == "strict":
        # We're going to be strict on enumeration prevention, and allow for
        # this email address to pass even though it already exists. In this
        # scenario, you can signup multiple times using the same email
        # address resulting in multiple accounts with an unverified email.
        return True
    else:
        assert app_settings.PREVENT_ENUMERATION is True
        # Conflict. We're supposed to prevent enumeration, but we can't
        # because that means letting the user in, while emails are required
        # to be unique. In this case, uniqueness takes precedence over
        # enumeration prevention.
        return False


def emit_email_changed(request, from_email_address, to_email_address):
    user = to_email_address.user
    signals.email_changed.send(
        sender=user.__class__,
        request=request,
        user=user,
        from_email_address=from_email_address,
        to_email_address=to_email_address,
    )
    if from_email_address:
        get_adapter().send_notification_mail(
            "account/email/email_changed",
            user,
            context={
                "from_email": from_email_address.email,
                "to_email": to_email_address.email,
            },
            email=from_email_address.email,
        )
