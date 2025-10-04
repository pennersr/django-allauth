from typing import Optional

from django.utils.functional import cached_property

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows.code_verification import (
    AbstractCodeVerificationProcess,
)
from allauth.account.internal.stagekit import clear_login
from allauth.account.internal.userkit import did_user_login, user_email
from allauth.account.models import EmailAddress
from allauth.core import context


EMAIL_VERIFICATION_CODE_SESSION_KEY = "account_email_verification_code"


class EmailVerificationProcess(AbstractCodeVerificationProcess):
    def __init__(self, request, state: dict, user=None) -> None:
        self.request = request
        super().__init__(
            state=state,
            user=user,
            max_attempts=app_settings.EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS,
            timeout=app_settings.EMAIL_VERIFICATION_BY_CODE_TIMEOUT,
        )

    @property
    def email(self) -> str:
        return self.state["email"]

    def persist(self) -> None:
        self.request.session[EMAIL_VERIFICATION_CODE_SESSION_KEY] = self.state

    def abort(self) -> None:
        self.request.session.pop(EMAIL_VERIFICATION_CODE_SESSION_KEY, None)
        clear_login(self.request)

    def send(self, skip_enumeration_mails: bool = False) -> None:
        from allauth.account.internal.flows.email_verification import (
            send_verification_email_to_address,
        )

        email_address = self.email_address
        signup = (
            (not did_user_login(email_address.user)) if email_address.user_id else True
        )
        self.did_send = send_verification_email_to_address(
            self.request,
            email_address,
            signup=signup,
            process=self,
            skip_enumeration_mails=skip_enumeration_mails,
        )

    @cached_property
    def email_address(self) -> EmailAddress:
        email = self.state["email"]
        if not self.user or self.state.get("account_already_exists"):
            return EmailAddress(email=email)
        try:
            email_address = EmailAddress.objects.get_for_user(self.user, email)
        except EmailAddress.DoesNotExist:
            email_address = EmailAddress(user=self.user, email=email)
        return email_address

    def finish(self) -> Optional[EmailAddress]:
        from allauth.account.internal.flows.email_verification import (
            mark_email_address_as_verified,
        )

        if not self.user or self.state.get("account_already_exists"):
            raise ValueError
        self.request.session.pop(EMAIL_VERIFICATION_CODE_SESSION_KEY, None)
        return mark_email_address_as_verified(self.request, self.email_address)

    def generate_code(self) -> None:
        self.state["code"] = get_adapter().generate_email_verification_code()

    @classmethod
    def initiate(cls, *, request, user, email: str) -> "EmailVerificationProcess":
        state = cls.initial_state(user, email)
        process = EmailVerificationProcess(request=request, user=user, state=state)
        process.generate_code()
        process.send()
        process.persist()
        return process

    @classmethod
    def resume(cls, request) -> Optional["EmailVerificationProcess"]:
        if not app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
            return None
        state = request.session.get(EMAIL_VERIFICATION_CODE_SESSION_KEY)
        if not state:
            return None
        process = EmailVerificationProcess(request=request, state=state)
        return process.abort_if_invalid()

    @property
    def can_change(self) -> bool:
        # TODO: Prevent enumeration flaw: if we don't have a user, we cannot
        # change the email. To fix this, we would need to serialize
        # the user and perform an on-the-fly signup here.
        return (
            not self.is_change_quota_reached(
                app_settings.EMAIL_VERIFICATION_MAX_CHANGE_COUNT
            )
            and bool(self.user)
            and not did_user_login(self.user)
        )

    def change_to(self, email: str, account_already_exists: bool) -> None:
        self.state["account_already_exists"] = account_already_exists
        self.generate_code()
        if account_already_exists:
            pass
        else:
            EmailAddress.objects.add_new_email(
                context.request, self.user, email, send_verification=False
            )
            user_email(self.user, email, commit=True)
        self.record_change(email=email)
        self.send()
        self.persist()

    @property
    def can_resend(self) -> bool:
        return not self.is_resend_quota_reached(
            app_settings.EMAIL_VERIFICATION_MAX_RESEND_COUNT
        )

    def resend(self) -> None:
        self.generate_code()
        self.send(skip_enumeration_mails=True)
        self.record_resend()
        self.persist()

    @property
    def key(self):
        return self.code
