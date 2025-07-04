from typing import Optional, Tuple

from django.contrib import messages
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows.manage_email import (
    emit_email_changed,
    sync_email_address,
    sync_user_email_address,
)
from allauth.account.internal.flows.signup import send_unknown_account_mail
from allauth.account.models import EmailAddress, Login
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.core.internal import ratelimit
from allauth.core.internal.httpkit import get_frontend_url
from allauth.core.ratelimit import respond_429
from allauth.utils import build_absolute_uri


def verify_email_indirectly(
    request: HttpRequest, user: AbstractBaseUser, email: str
) -> bool:
    try:
        email_address = EmailAddress.objects.get_for_user(user, email)
    except EmailAddress.DoesNotExist:
        return False
    else:
        if not email_address.verified:
            return verify_email(request, email_address)
        return True


def verify_email_and_resume(
    request: HttpRequest, verification
) -> Tuple[Optional[EmailAddress], Optional[HttpResponse]]:
    email_address = verification.confirm(request)
    if not email_address:
        return None, None
    response = login_on_verification(request, email_address)
    return email_address, response


def verify_email(request: HttpRequest, email_address: EmailAddress) -> bool:
    """
    Marks the email address as confirmed on the db
    """
    added = not email_address.pk
    from_email_address = (
        EmailAddress.objects.filter(user_id=email_address.user_id)
        .exclude(pk=email_address.pk)
        .first()
    )
    if not email_address.set_verified(commit=False):
        get_adapter(request).add_message(
            request,
            messages.ERROR,
            "account/messages/email_confirmation_failed.txt",
            {"email": email_address.email},
        )
        return False
    email_address.set_as_primary(conditional=(not app_settings.CHANGE_EMAIL))
    email_address.save()
    if added:
        signals.email_added.send(
            sender=EmailAddress,
            request=request,
            user=request.user,
            email_address=email_address,
        )
    signals.email_confirmed.send(
        sender=EmailAddress,
        request=request,
        email_address=email_address,
    )
    if app_settings.CHANGE_EMAIL:
        for instance in EmailAddress.objects.filter(
            user_id=email_address.user_id
        ).exclude(pk=email_address.pk):
            instance.remove()
        emit_email_changed(request, from_email_address, email_address)
    get_adapter(request).add_message(
        request,
        messages.SUCCESS,
        "account/messages/email_confirmed.txt",
        {"email": email_address.email},
    )
    return True


def get_email_verification_url(request: HttpRequest, emailconfirmation) -> str:
    """Constructs the email confirmation (activation) url.

    Note that if you have architected your system such that email
    confirmations are sent outside of the request context `request`
    can be `None` here.
    """
    url = get_frontend_url(request, "account_confirm_email", key=emailconfirmation.key)
    if not url:
        url = reverse("account_confirm_email", args=[emailconfirmation.key])
        url = build_absolute_uri(request, url)
    return url


def login_on_verification(request, email_address) -> Optional[HttpResponse]:
    """Simply logging in the user may become a security issue. If you
    do not take proper care (e.g. don't purge used email
    confirmations), a malicious person that got hold of the link
    will be able to login over and over again and the user is
    unable to do anything about it. Even restoring their own mailbox
    security will not help, as the links will still work. For
    password reset this is different, this mechanism works only as
    long as the attacker has access to the mailbox. If they no
    longer has access they cannot issue a password request and
    intercept it. Furthermore, all places where the links are
    listed (log files, but even Google Analytics) all of a sudden
    need to be secured. Purging the email confirmation once
    confirmed changes the behavior -- users will not be able to
    repeatedly confirm (in case they forgot that they already
    clicked the mail).

    All in all, we only login on verification when the user that is in the
    process of signing up is present in the session to avoid all of the above.
    This may not 100% work in case the user closes the browser (and the session
    gets lost), but at least we're secure.
    """
    from allauth.account.stages import EmailVerificationStage, LoginStageController

    stage = LoginStageController.enter(request, EmailVerificationStage.key)
    if (
        (
            # Logging in on email verification is disabled...
            not app_settings.LOGIN_ON_EMAIL_CONFIRMATION
            # (but, that is only relevant for verification-by-link)
            and not app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED
        )
        or (request.user.is_authenticated)
        or (not stage or not stage.login.user)
        or (stage.login.user.pk != email_address.user_id)
    ):
        if stage:
            stage.abort()
        return None
    return stage.exit()


def consume_email_verification_rate_limit(
    request: HttpRequest,
    email: str,
    dry_run: bool = False,
    raise_exception: bool = False,
) -> bool:
    return bool(
        ratelimit.consume(
            request,
            config=app_settings.RATE_LIMITS,
            action="confirm_email",
            key=email.lower(),
            dry_run=dry_run,
            raise_exception=raise_exception,
            limit_get=True,
        )
    )


def handle_verification_email_rate_limit(
    request, email: str, raise_exception: bool = False
) -> bool:
    """
    For email verification by link, it is not an issue if the user runs into rate
    limits. The reason is that the link is session independent. Therefore, if the
    user hits rate limits, we can just silently skip sending additional
    verification emails, as the previous emails that were already sent still
    contain valid links. This is different from email verification by code.  Here,
    the session contains a specific code, meaning, silently skipping new
    verification emails is not an option, and we must hard fail (429) instead. The
    latter was missing, fixed.
    """
    rl_ok = consume_email_verification_rate_limit(
        request, email, raise_exception=raise_exception
    )
    if not rl_ok and app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
        raise ImmediateHttpResponse(respond_429(request))
    return rl_ok


def get_address_for_user(user: AbstractBaseUser) -> Optional[EmailAddress]:
    address = (
        EmailAddress.objects.filter(user_id=user.pk)
        .order_by("-primary", "-verified")
        .first()
    )
    if not address:
        address = sync_user_email_address(user)
    return address


def get_address_for_login(login: Login):
    assert login.user  # nosec
    if login.email:
        try:
            return EmailAddress.objects.get_for_user(login.user, login.email)
        except EmailAddress.DoesNotExist:
            # We do have an email, it's not stored as an EmailAddress. Might be the
            # case that a user was setup in the admin. So, let's sync
            # EmailAddress'es on the fly here.
            return sync_email_address(login.user, login.email)
    else:
        return get_address_for_user(login.user)


def send_verification_email_for_user(
    request: HttpRequest, user: AbstractBaseUser
) -> bool:
    """
    Used in the email-required-decorator.
    """
    address = get_address_for_user(user)
    if not address:
        return False
    return send_verification_email_to_address(request, address)


def send_verification_email_to_address(
    request: HttpRequest,
    address: EmailAddress,
    signup: bool = False,
    process=None,
    skip_enumeration_mails: bool = False,
) -> bool:
    """
    Resend email verification for an existing email address.
    """
    if app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
        if not process:
            from allauth.account.internal.flows.email_verification_by_code import (
                EmailVerificationProcess,
            )

            process = EmailVerificationProcess.initiate(
                request=request,
                user=address.user if address.user_id else None,
                email=address.email,
            )
            return process.did_send

    send = handle_verification_email_rate_limit(
        request,
        address.email,
    )
    if not send:
        return False

    if not address.user_id:
        if skip_enumeration_mails:
            pass
        elif signup:
            get_adapter().send_account_already_exists_mail(address.email)
        else:
            send_unknown_account_mail(request, address.email)
        confirmation = None
    elif app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
        get_adapter().send_confirmation_mail(request, process, signup=signup)
        confirmation = process
    else:
        confirmation = address.send_confirmation(request, signup=signup)
    add_email_verification_sent_message(request, address.email, signup=signup)
    if confirmation:
        signals.email_confirmation_sent.send(
            sender=confirmation.__class__,
            request=request,
            confirmation=confirmation,
            signup=signup,
        )
    return True


def send_verification_email_at_login(request: HttpRequest, login: Login) -> bool:
    """
    At this point, it has already been confirmed that email verification
    is needed.

    Email verification mails are sent:
    a) Explicitly: when a user signs up
    b) Implicitly: when a user attempts to log in using an unverified
    email while EMAIL_VERIFICATION is mandatory.
    """
    if not login.user:
        sent = send_verification_email_at_fake_login(request, login)
    else:
        sent = send_verification_email_at_real_login(request, login)
    return sent


def send_verification_email_at_real_login(request: HttpRequest, login: Login) -> bool:
    assert login.user  # nosec
    address = get_address_for_login(login)
    if not address:
        return False
    if address.verified:
        return False
    send = get_adapter().should_send_confirmation_mail(request, address, login.signup)
    if not send:
        return False
    return send_verification_email_to_address(request, address, signup=login.signup)


def send_verification_email_at_fake_login(request: HttpRequest, login: Login) -> bool:
    """
    Enumeration prevention.
    """
    assert not login.user  # nosec
    if not login.email:
        # Odd, no user & no email implies email enumeration prevention is
        # active, at signup, which implies we should have an email here?
        return False
    address = EmailAddress(user=None, email=login.email)
    return send_verification_email_to_address(request, address, signup=True)


def add_email_verification_sent_message(request: HttpRequest, email: str, signup: bool):
    get_adapter().add_message(
        request,
        messages.INFO,
        "account/messages/email_confirmation_sent.txt",
        {"email": email, "login": not signup, "signup": signup},
    )


def is_verification_rate_limited(request: HttpRequest, login: Login) -> bool:
    """
    Returns whether or not the email verification is *hard* rate limited.
    Hard, meaning, it would be blocking login (verification by code, not link).
    """
    if (
        (not login.email)
        or (not app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED)
        or login.email_verification != app_settings.EmailVerificationMethod.MANDATORY
    ):
        return False
    try:
        email_address = EmailAddress.objects.get_for_user(login.user, login.email)
        if not email_address.verified:
            if not consume_email_verification_rate_limit(
                request, login.email, dry_run=True
            ):
                return True
    except EmailAddress.DoesNotExist:
        pass
    return False


def mark_email_address_as_verified(
    request: HttpRequest, address: EmailAddress
) -> Optional[EmailAddress]:
    if not address.verified:
        confirmed = get_adapter().confirm_email(request, address)
        if confirmed:
            return address
    return None
