from typing import Optional, Tuple

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
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
    from allauth.account.models import EmailAddress
    from allauth.account.utils import emit_email_changed

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
    if app_settings.CHANGE_EMAIL:
        for instance in EmailAddress.objects.filter(
            user_id=email_address.user_id
        ).exclude(pk=email_address.pk):
            instance.remove()
        emit_email_changed(request, from_email_address, email_address)

    signals.email_confirmed.send(
        sender=EmailAddress,
        request=request,
        email_address=email_address,
    )
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

    if not app_settings.LOGIN_ON_EMAIL_CONFIRMATION:
        return None
    if request.user.is_authenticated:
        return None
    stage = LoginStageController.enter(request, EmailVerificationStage.key)
    if not stage or not stage.login.user:
        return None
    if stage.login.user.pk != verification.email_address.user_id:
        return None
    return stage.exit()
