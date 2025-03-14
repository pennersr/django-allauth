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
from allauth.account.internal.userkit import user_id_to_str
from allauth.core import context


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
    def phone(self):
        return self.state["phone"]

    def send(self):
        adapter = get_adapter()
        code = adapter.generate_phone_verification_code()
        adapter.send_verification_code_sms(
            user=self.user,
            code=code,
            phone=self.state["phone"],
        )
        self.state.update({"code": code, "user_id": user_id_to_str(self.user)})
        self.persist()

    def finish(self):
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
        process.send()
        return process

    @classmethod
    def resume(cls, stage) -> Optional["PhoneVerificationStageProcess"]:
        state = stage.state
        if not state:
            return None
        process = PhoneVerificationStageProcess(stage)
        return process.abort_if_invalid()


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
