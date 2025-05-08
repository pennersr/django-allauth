from typing import Optional

from django.contrib import messages
from django.http import HttpRequest

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows.code_verification import (
    AbstractCodeVerificationProcess,
)
from allauth.account.internal.flows.reauthentication import (
    raise_if_reauthentication_required,
)
from allauth.account.internal.stagekit import stash_login
from allauth.account.internal.userkit import did_user_login
from allauth.core import context, ratelimit


PHONE_VERIFICATION_STATE_KEY = "phone_verification"
PHONE_VERIFICATION_SESSION_KEY = "account_phone_verification"


def verify_phone_indirectly(request: HttpRequest, user, phone: str) -> None:
    get_adapter().set_phone_verified(user, phone)


class PhoneVerificationProcess(AbstractCodeVerificationProcess):
    def __init__(self, user, state):
        super().__init__(
            user=user,
            state=state,
            timeout=app_settings.PHONE_VERIFICATION_TIMEOUT,
            max_attempts=app_settings.PHONE_VERIFICATION_MAX_ATTEMPTS,
        )

    @property
    def phone(self) -> str:
        return self.state["phone"]

    def send(self, skip_enumeration_sms: bool = False) -> None:
        ratelimit.consume(
            context.request,
            action="verify_phone",
            key=self.phone,
            raise_exception=True,
        )
        adapter = get_adapter()
        code = adapter.generate_phone_verification_code()
        self.state["code"] = code
        self.send_sms(skip_enumeration_sms)
        get_adapter().add_message(
            context.request,
            messages.INFO,
            "account/messages/phone_verification_sent.txt",
            {"phone": self.phone},
        )
        self.persist()

    def send_sms(self, skip_enumeration_sms: bool) -> None:
        adapter = get_adapter()
        if not self.user or self.state.get("account_already_exists"):
            if not skip_enumeration_sms:
                if self.state.get("account_already_exists") or self.state.get("signup"):
                    adapter.send_account_already_exists_sms(self.phone)
                else:
                    adapter.send_unknown_account_sms(self.phone)
            return
        adapter.send_verification_code_sms(
            user=self.user,
            code=self.code,
            phone=self.phone,
        )

    def finish(self) -> None:
        phone = self.state["phone"]
        adapter = get_adapter()
        adapter.set_phone_verified(self.user, phone)
        adapter.add_message(
            context.request,
            messages.SUCCESS,
            "account/messages/phone_verified.txt",
            {"phone": phone},
        )


class PhoneVerificationStageProcess(PhoneVerificationProcess):
    def __init__(self, stage):
        self.stage = stage
        super().__init__(user=stage.login.user, state=stage.state)

    def abort(self):
        pass

    def persist(self):
        stash_login(self.stage.request, self.stage.login)

    @classmethod
    def initiate(cls, *, stage, phone: str):
        stage.state.update(cls.initial_state(user=stage.login.user, phone=phone))
        process = PhoneVerificationStageProcess(stage=stage)
        process.state["signup"] = stage.login.signup
        process.send(skip_enumeration_sms=False)
        return process

    @classmethod
    def resume(cls, stage) -> Optional["PhoneVerificationStageProcess"]:
        state = stage.state
        if not state:
            return None
        process = PhoneVerificationStageProcess(stage)
        return process.abort_if_invalid()

    def change_to(self, phone: str, account_already_exists: bool) -> None:
        self.state["account_already_exists"] = account_already_exists
        self.record_change(phone=phone)
        adapter = get_adapter()
        if not account_already_exists:
            adapter.set_phone(self.user, phone, False)
        self.send(skip_enumeration_sms=False)
        self.persist()

    def resend(self):
        self.record_resend()
        self.send(skip_enumeration_sms=True)

    @property
    def can_resend(self) -> bool:
        return not self.is_resend_quota_reached(
            app_settings.PHONE_VERIFICATION_MAX_RESEND_COUNT
        )

    @property
    def can_change(self) -> bool:
        # TODO: Prevent enumeration flaw: if we don't have a user, we cannot
        # change the phone. To fix this, we would need to serialize
        # the user and perform an on-the-fly signup here.
        return (
            not self.is_change_quota_reached(
                app_settings.PHONE_VERIFICATION_MAX_CHANGE_COUNT
            )
            and bool(self.user)
            and not did_user_login(self.user)
        )


class ChangePhoneVerificationProcess(PhoneVerificationProcess):
    def __init__(self, request: HttpRequest, state: dict):
        self.request = request
        super().__init__(
            user=request.user,
            state=state,
        )

    def abort(self):
        self.request.session.pop(PHONE_VERIFICATION_SESSION_KEY, None)

    def persist(self):
        self.request.session[PHONE_VERIFICATION_SESSION_KEY] = self.state

    def finish(self):
        super().finish()
        self.request.session.pop(PHONE_VERIFICATION_SESSION_KEY, None)

    @classmethod
    def initiate(cls, request: HttpRequest, phone: str):
        if app_settings.REAUTHENTICATION_REQUIRED:
            raise_if_reauthentication_required(request)

        state = cls.initial_state(user=request.user, phone=phone)
        process = ChangePhoneVerificationProcess(request, state=state)
        process.send()
        return process

    @classmethod
    def resume(cls, request: HttpRequest) -> Optional["ChangePhoneVerificationProcess"]:
        state = request.session.get(PHONE_VERIFICATION_SESSION_KEY)
        if not state:
            return None
        process = ChangePhoneVerificationProcess(request, state=state)
        return process.abort_if_invalid()


def phone_already_exists(user, phone: str, always_raise: bool = False) -> bool:
    """
    Throws a validation error (if allowed by enumeration prevention rules).
    Otherwise, returns True iff another account already exists.
    """
    adapter = get_adapter()
    other_user = adapter.get_user_by_phone(phone)
    already_exists = other_user and (not user or user.pk != other_user.pk)
    if already_exists and (not app_settings.PREVENT_ENUMERATION or always_raise):
        raise adapter.validation_error("phone_taken")
    return already_exists
