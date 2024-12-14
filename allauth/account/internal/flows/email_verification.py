from typing import Optional, Tuple

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows.manage_email import emit_email_changed
from allauth.account.models import EmailAddress, Login
from allauth.core import ratelimit
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.core.internal.httpkit import get_frontend_url
from allauth.utils import build_absolute_uri


def verify_email_indirectly(request: HttpRequest, user, email: str) -> bool:
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
    response = login_on_verification(request, verification)
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


def login_on_verification(request, verification) -> Optional[HttpResponse]:
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
    from allauth.account.stages import (
        EmailVerificationStage,
        LoginStageController,
    )

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
        or (stage.login.user.pk != verification.email_address.user_id)
    ):
        if stage:
            stage.abort()
        return None
    return stage.exit()


def consume_email_verification_rate_limit(
    request: HttpRequest, email: str, dry_run: bool = False
) -> bool:
    return ratelimit.consume(
        request, action="confirm_email", key=email.lower(), dry_run=dry_run
    )


def handle_verification_email_rate_limit(request, email: str) -> bool:
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
    rl_ok = consume_email_verification_rate_limit(request, email)
    if not rl_ok and app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
        raise ImmediateHttpResponse(ratelimit.respond_429(request))
    return rl_ok


def send_verification_email(request, user, signup=False, email=None) -> bool:
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
    from allauth.account.utils import user_email

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
                send_email = handle_verification_email_rate_limit(
                    request, email_address.email
                )
                if send_email:
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
            assert email_address  # nosec
        # At this point, if we were supposed to send an email we have sent it.
        if send_email:
            adapter.add_message(
                request,
                messages.INFO,
                "account/messages/email_confirmation_sent.txt",
                {"email": email, "login": not signup, "signup": signup},
            )
    return sent


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
