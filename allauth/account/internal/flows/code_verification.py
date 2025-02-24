import abc
import time
from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model

from allauth.account.internal.userkit import str_to_user_id, user_id_to_str


class AbstractCodeVerificationProcess(abc.ABC):
    def __init__(
        self,
        max_attempts: int,
        timeout: int,
        state: dict,
        user=None,
    ) -> None:
        self._user = user
        self.max_attempts = max_attempts
        self.timeout = timeout
        self.state = state

    @property
    def user(self):
        if self._user:
            return self._user
        user_id = self.state.get("user_id")
        if not user_id:
            return None
        user_id = str_to_user_id(user_id)
        self._user = get_user_model().objects.filter(pk=user_id).first()
        return self._user

    @property
    def code(self):
        return self.state.get("code", "")

    @classmethod
    def initial_state(
        cls, user, email: Optional[str] = None, phone: Optional[str] = None
    ):
        state: Dict[str, Any] = {
            "at": time.time(),
            "failed_attempts": 0,
        }
        if email:
            state["email"] = email
        if phone:
            state["phone"] = phone
        if user:
            state["user_id"] = user_id_to_str(user)
        return state

    def record_invalid_attempt(self) -> bool:
        self.state["failed_attempts"] += 1
        if self.state["failed_attempts"] >= self.max_attempts:
            self.abort()
            return False
        self.persist()
        return True

    def abort_if_invalid(self):
        if not self.is_valid():
            self.abort()
            return None
        return self

    def is_valid(self) -> bool:
        return time.time() - self.state["at"] <= self.timeout

    @abc.abstractmethod
    def persist(self): ...  # noqa: E704

    @abc.abstractmethod
    def send(self): ...  # noqa: E704

    @abc.abstractmethod
    def abort(self): ...  # noqa: E704
