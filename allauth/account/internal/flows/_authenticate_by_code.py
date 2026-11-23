from typing import Any

from django.contrib import messages
from django.http import HttpRequest

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows.code_verification import (
    AbstractCodeVerificationProcess,
)
from allauth.account.internal.flows.signup import send_unknown_account_mail


class BaseConfirmAuthenticationCodeProcess(AbstractCodeVerificationProcess):
    request: HttpRequest
    stage: Any
    reauthentication: bool = False

    def send(self, skip_enumeration_mails: bool = False) -> None:
        email = self.state.get("email")
        phone = self.state.get("phone")
        if email:
            self.send_by_email(email, skip_enumeration_mails=skip_enumeration_mails)
        elif phone:
            self.send_by_phone(phone, skip_enumeration_mails=skip_enumeration_mails)
        else:
            raise ValueError()

    def generate_code(self) -> str:
        email = self.state.get("email")
        phone = self.state.get("phone")
        adapter = get_adapter()
        if email:
            code = adapter.generate_login_code()
        elif phone:
            assert self.user  # nosec
            code = adapter._generate_phone_verification_code_compat(
                user=self.user, phone=phone
            )
        else:
            raise ValueError()
        self.state["code"] = code
        return code

    def send_by_phone(self, phone: str, skip_enumeration_mails: bool = False) -> None:
        adapter = get_adapter()
        if self.user:
            code = self.generate_code()
            adapter.send_verification_code_sms(
                user=self.user,
                phone=phone,
                code=code,
                reauthentication=self.reauthentication,
            )
        elif not skip_enumeration_mails:
            if self.stage.login.signup:
                adapter.send_account_already_exists_sms(phone)
            else:
                adapter.send_unknown_account_sms(phone)
        self.add_sent_message({"recipient": phone, "phone": phone})

    def send_by_email(self, email: str, skip_enumeration_mails: bool = False) -> None:
        adapter = get_adapter()
        if self.user:
            code = self.generate_code()
            context = {
                "request": self.request,
                "code": code,
                "reauthentication": self.reauthentication,
            }
            adapter.send_mail("account/email/login_code", email, context)
        elif not skip_enumeration_mails:
            if self.stage.login.signup:
                adapter.send_account_already_exists_mail(email)
            else:
                send_unknown_account_mail(self.request, email)
        self.add_sent_message(
            {
                "email": email,
                "recipient": email,
            }
        )

    def add_sent_message(self, context) -> None:
        context["reauthentication"] = self.reauthentication
        get_adapter().add_message(
            self.request,
            messages.SUCCESS,
            "account/messages/login_code_sent.txt",
            context,
        )

    @property
    def can_resend(self) -> bool:
        return not self.is_resend_quota_reached(
            app_settings.LOGIN_BY_CODE_MAX_RESEND_COUNT
        )

    def resend(self) -> None:
        with self.state_transaction():
            self.generate_code()
            self.send(skip_enumeration_mails=True)
        self.record_resend()
        self.persist()
