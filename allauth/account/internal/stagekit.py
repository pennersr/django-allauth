from __future__ import annotations

import time

from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from allauth.account import app_settings
from allauth.account.models import Login
from allauth.account.stages import LoginStage, LoginStageController


LOGIN_SESSION_KEY = "account_login"


def get_pending_stage(request: HttpRequest) -> LoginStage | None:
    stage = None
    if not request.user.is_authenticated:
        login = unstash_login(request, peek=True)
        if login:
            ctrl = LoginStageController(request, login)
            stage = ctrl.get_pending_stage()
    return stage


def redirect_to_pending_stage(
    request: HttpRequest, stage: LoginStage
) -> HttpResponseRedirect:
    if stage.urlname:
        return HttpResponseRedirect(reverse(stage.urlname))
    clear_login(request)
    return HttpResponseRedirect(reverse("account_login"))


def clear_login(request: HttpRequest) -> None:
    request.session.pop(LOGIN_SESSION_KEY, None)


def unstash_login(request: HttpRequest, peek: bool = False) -> Login | None:
    login = None
    if peek:
        data = request.session.get(LOGIN_SESSION_KEY)
    else:
        data = request.session.pop(LOGIN_SESSION_KEY, None)
    if isinstance(data, dict):
        try:
            login = Login.deserialize(data)
        except ValueError:
            pass
        else:
            if time.time() - login.initiated_at > app_settings.LOGIN_TIMEOUT:
                login = None
                clear_login(request)
            else:
                request._account_login_accessed = True  # type:ignore[attr-defined]
    return login


def stash_login(request: HttpRequest, login) -> None:
    request.session[LOGIN_SESSION_KEY] = login.serialize()
    request._account_login_accessed = True  # type:ignore[attr-defined]
