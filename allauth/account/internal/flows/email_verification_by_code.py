from typing import Optional

from django.utils.functional import cached_property

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows.code_verification import (
    AbstractCodeVerificationProcess,
)
from allauth.account.internal.stagekit import clear_login
from allauth.account.models import EmailAddress, EmailConfirmationMixin
from allauth.core import context


EMAIL_VERIFICATION_CODE_SESSION_KEY = "account_email_verification_code"


class EmailVerificationModel(EmailConfirmationMixin):
    def __init__(self, email_address: EmailAddress, key: Optional[str] = None):
        self.email_address = email_address
        if not key:
            process = EmailVerificationProcess.initiate(
                request=context.request,
                user=email_address.user,
                email=email_address.email,
            )
            key = process.code
        self.key = key

    @classmethod
    def create(cls, email_address: EmailAddress):
        return EmailVerificationModel(email_address)

    @classmethod
    def from_key(cls, key):
        raise NotImplementedError

    def key_expired(self):
        raise NotImplementedError


class EmailVerificationProcess(AbstractCodeVerificationProcess):
    def __init__(self, request, state, user=None):
        self.request = request
        super().__init__(
            state=state,
            user=user,
            max_attempts=app_settings.EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS,
            timeout=app_settings.EMAIL_VERIFICATION_BY_CODE_TIMEOUT,
        )

    def persist(self):
        self.request.session[EMAIL_VERIFICATION_CODE_SESSION_KEY] = self.state

    def abort(self):
        self.request.session.pop(EMAIL_VERIFICATION_CODE_SESSION_KEY, None)
        clear_login(self.request)

    def send(self):
        self.state["code"] = get_adapter().generate_email_verification_code()

    @cached_property
    def email_address(self):
        user = self.user
        email = self.state["email"]
        try:
            email_address = EmailAddress.objects.get_for_user(user, email)
        except EmailAddress.DoesNotExist:
            email_address = EmailAddress(user=user, email=email)
        return email_address

    def finish(self):
        verification = EmailVerificationModel(
            self.email_address, key=self.state["code"]
        )
        self.request.session.pop(EMAIL_VERIFICATION_CODE_SESSION_KEY, None)
        return verification.confirm(self.request)

    @classmethod
    def initiate(cls, *, request, user, email: str):
        state = cls.initial_state(user, email)
        process = EmailVerificationProcess(request=request, user=user, state=state)
        process.send()
        process.persist()
        return process

    @classmethod
    def resume(cls, request):
        state = request.session.get(EMAIL_VERIFICATION_CODE_SESSION_KEY)
        if not state:
            return None
        process = EmailVerificationProcess(request=request, state=state)
        return process.abort_if_invalid()
