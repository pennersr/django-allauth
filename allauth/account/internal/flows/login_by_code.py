import time
from typing import Any, Dict, Optional, Tuple

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.internal.flows.email_verification import (
    verify_email_indirectly,
)
from allauth.account.internal.flows.login import (
    perform_login,
    record_authentication,
)
from allauth.account.internal.flows.signup import send_unknown_account_mail
from allauth.account.internal.stagekit import clear_login, stash_login
from allauth.account.models import Login


LOGIN_CODE_STATE_KEY = "login_code"


def request_login_code(
    request: HttpRequest, email: str, login: Optional[Login] = None
) -> None:
    from allauth.account.utils import filter_users_by_email

    initiated_by_user = login is None
    adapter = get_adapter()
    users = filter_users_by_email(email, is_active=True, prefer_verified=True)
    pending_login = {
        "at": time.time(),
        "email": email,
        "failed_attempts": 0,
        "initiated_by_user": initiated_by_user,
    }
    if not users:
        user = None
        send_unknown_account_mail(request, email)
    else:
        user = users[0]
        code = adapter.generate_login_code()
        context = {
            "request": request,
            "code": code,
        }
        adapter.send_mail("account/email/login_code", email, context)
        pending_login.update(
            {"code": code, "user_id": user._meta.pk.value_to_string(user)}
        )
    adapter.add_message(
        request,
        messages.SUCCESS,
        "account/messages/login_code_sent.txt",
        {"email": email},
    )
    if initiated_by_user:
        login = Login(user=user, email=email)
        login.state["stages"] = {"current": "login_by_code"}
    assert login  # nosec
    login.state[LOGIN_CODE_STATE_KEY] = pending_login
    if initiated_by_user:
        stash_login(request, login)


def get_pending_login(
    request, login: Login, peek: bool = False
) -> Tuple[Optional[AbstractBaseUser], Optional[Dict[str, Any]]]:
    if peek:
        data = login.state.get(LOGIN_CODE_STATE_KEY)
    else:
        data = login.state.pop(LOGIN_CODE_STATE_KEY, None)
    if not data:
        return None, None
    if time.time() - data["at"] >= app_settings.LOGIN_BY_CODE_TIMEOUT:
        login.state.pop(LOGIN_CODE_STATE_KEY, None)
        clear_login(request)
        return None, None
    user_id_str = data.get("user_id")
    user = None
    if user_id_str:
        user_id = get_user_model()._meta.pk.to_python(user_id_str)  # type: ignore[union-attr]
        user = get_user_model().objects.get(pk=user_id)
    return user, data


def record_invalid_attempt(request, login: Login) -> bool:
    from allauth.account.internal.stagekit import stash_login, unstash_login

    pending_login = login.state[LOGIN_CODE_STATE_KEY]
    n = pending_login["failed_attempts"]
    n += 1
    pending_login["failed_attempts"] = n
    if n >= app_settings.LOGIN_BY_CODE_MAX_ATTEMPTS:
        unstash_login(request)
        return False
    else:
        login.state[LOGIN_CODE_STATE_KEY] = pending_login
        stash_login(request, login)
        return True


def perform_login_by_code(
    request: HttpRequest,
    stage,
    redirect_url: Optional[str],
):
    state = stage.login.state[LOGIN_CODE_STATE_KEY]
    email = state["email"]
    user = stage.login.user
    record_authentication(request, method="code", email=email)
    verify_email_indirectly(request, user, email)
    if state["initiated_by_user"]:
        # Just requesting a login code does is not considered to be a real login,
        # yet, is needed in order to make the stage machinery work. Now that we've
        # completed the code, let's start a real login.
        login = Login(
            user=user,
            redirect_url=redirect_url,
            email=email,
        )
        return perform_login(request, login)
    else:
        return stage.exit()


def compare_code(*, actual, expected) -> bool:
    actual = actual.replace(" ", "").lower()
    expected = expected.replace(" ", "").lower()
    return expected and actual == expected
