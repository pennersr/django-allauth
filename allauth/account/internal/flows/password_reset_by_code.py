from __future__ import annotations

from typing import Optional

from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest, HttpResponse

from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows import password_reset
from allauth.account.internal.flows.code_verification import (
    AbstractCodeVerificationProcess,
)
from allauth.account.internal.flows.email_verification import verify_email_indirectly
from allauth.account.internal.flows.signup import send_unknown_account_mail


PASSWORD_RESET_VERIFICATION_SESSION_KEY = (
    "account_password_reset_verification"  # nosec: B105
)


class PasswordResetVerificationProcess(AbstractCodeVerificationProcess):
    def __init__(
        self, request: HttpRequest, state, user: AbstractBaseUser | None = None
    ) -> None:
        self.request = request
        super().__init__(
            state=state,
            timeout=app_settings.PASSWORD_RESET_BY_CODE_TIMEOUT,
            max_attempts=app_settings.PASSWORD_RESET_BY_CODE_MAX_ATTEMPTS,
            user=user,
        )

    def record_invalid_attempt(self) -> bool:
        has_attempts_left = super().record_invalid_attempt()
        if self.user:
            signals.password_reset_code_rejected.send(
                sender=PasswordResetVerificationProcess,
                request=self.request,
                user=self.user,
                last_attempt=not has_attempts_left,
            )
        return has_attempts_left

    def abort(self) -> None:
        self.request.session.pop(PASSWORD_RESET_VERIFICATION_SESSION_KEY, None)

    def confirm_code(self) -> None:
        if self.state.get("code_confirmed"):
            return
        self.state["code_confirmed"] = True
        self.persist()
        assert self.user  # nosec
        verify_email_indirectly(self.request, self.user, self.state["email"])

    def finish(self) -> HttpResponse | None:
        self.request.session.pop(PASSWORD_RESET_VERIFICATION_SESSION_KEY, None)
        assert self.user  # nosec
        return password_reset.finalize_password_reset(
            self.request, self.user, email=self.state["email"]
        )

    def persist(self) -> None:
        self.request.session[PASSWORD_RESET_VERIFICATION_SESSION_KEY] = self.state

    def send(self) -> None:
        adapter = get_adapter()
        email = self.state["email"]
        if not self.user:
            send_unknown_account_mail(self.request, email)
            return
        code = adapter.generate_password_reset_code()
        self.state["code"] = code
        context = {
            "request": self.request,
            "code": self.code,
        }
        adapter.send_mail("account/email/password_reset_code", email, context)

    @classmethod
    def initiate(
        cls, *, request: HttpRequest, user: AbstractBaseUser | None, email: str
    ) -> PasswordResetVerificationProcess:
        state = cls.initial_state(user, email)
        process = PasswordResetVerificationProcess(request, state=state, user=user)
        process.send()
        process.persist()
        return process

    @classmethod
    def resume(
        cls, request: HttpRequest
    ) -> Optional["PasswordResetVerificationProcess"]:
        state = request.session.get(PASSWORD_RESET_VERIFICATION_SESSION_KEY)
        if not state:
            return None
        process = PasswordResetVerificationProcess(request, state=state)
        return process.abort_if_invalid()
