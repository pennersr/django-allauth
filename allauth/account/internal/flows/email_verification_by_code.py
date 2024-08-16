import time
from typing import Any, Dict, Optional, Tuple

from django.contrib.auth import get_user_model
from django.http import HttpRequest

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows.login_by_code import compare_code
from allauth.account.models import EmailAddress, EmailConfirmationMixin
from allauth.core import context


EMAIL_VERIFICATION_CODE_SESSION_KEY = "account_email_verification_code"


class EmailVerificationModel(EmailConfirmationMixin):
    def __init__(self, email_address: EmailAddress, key: Optional[str] = None):
        self.email_address = email_address
        if not key:
            key = request_email_verification_code(
                context.request, user=email_address.user, email=email_address.email
            )
        self.key = key

    @classmethod
    def create(cls, email_address: EmailAddress):
        return EmailVerificationModel(email_address)

    @classmethod
    def from_key(cls, key):
        verification, _ = get_pending_verification(context.request, peek=True)
        if not verification or not compare_code(actual=key, expected=verification.key):
            return None
        return verification

    def key_expired(self):
        return False


def request_email_verification_code(
    request: HttpRequest,
    user,
    email: str,
) -> str:
    code = ""
    pending_verification = {
        "at": time.time(),
        "failed_attempts": 0,
        "email": email,
    }
    pretend = user is None
    if not pretend:
        adapter = get_adapter()
        code = adapter.generate_email_verification_code()
        assert user._meta.pk
        pending_verification.update(
            {
                "user_id": user._meta.pk.value_to_string(user),
                "email": email,
                "code": code,
            }
        )
    request.session[EMAIL_VERIFICATION_CODE_SESSION_KEY] = pending_verification
    return code


def get_pending_verification(
    request: HttpRequest, peek: bool = False
) -> Tuple[Optional[EmailVerificationModel], Optional[Dict[str, Any]]]:
    if peek:
        data = request.session.get(EMAIL_VERIFICATION_CODE_SESSION_KEY)
    else:
        data = request.session.pop(EMAIL_VERIFICATION_CODE_SESSION_KEY, None)
    if not data:
        return None, None
    if time.time() - data["at"] >= app_settings.EMAIL_VERIFICATION_BY_CODE_TIMEOUT:
        request.session.pop(EMAIL_VERIFICATION_CODE_SESSION_KEY, None)
        return None, None
    if user_id_str := data.get("user_id"):
        user_id = get_user_model()._meta.pk.to_python(user_id_str)  # type: ignore[union-attr]
        user = get_user_model().objects.get(pk=user_id)
        email = data["email"]
        try:
            email_address = EmailAddress.objects.get_for_user(user, email)
        except EmailAddress.DoesNotExist:
            email_address = EmailAddress(user=user, email=email)
        verification = EmailVerificationModel(email_address, key=data["code"])
    else:
        verification = None
    return verification, data


def record_invalid_attempt(
    request: HttpRequest, pending_verification: Dict[str, Any]
) -> bool:
    n = pending_verification["failed_attempts"]
    n += 1
    pending_verification["failed_attempts"] = n
    if n >= app_settings.EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS:
        request.session.pop(EMAIL_VERIFICATION_CODE_SESSION_KEY, None)
        return False
    else:
        request.session[EMAIL_VERIFICATION_CODE_SESSION_KEY] = pending_verification
        return True
