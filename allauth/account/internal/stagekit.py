import time
from typing import Optional

from django.http import HttpResponseRedirect
from django.urls import reverse

from allauth.account import app_settings
from allauth.account.models import Login
from allauth.account.stages import LoginStage, LoginStageController


LOGIN_SESSION_KEY = "account_login"


def get_pending_stage(request) -> Optional[LoginStage]:
    stage = None
    if not request.user.is_authenticated:
        login = unstash_login(request, peek=True)
        if login:
            ctrl = LoginStageController(request, login)
            stage = ctrl.get_pending_stage()
    return stage


def redirect_to_pending_stage(request, stage: LoginStage):
    if stage.urlname:
        return HttpResponseRedirect(reverse(stage.urlname))
    clear_login(request)
    return HttpResponseRedirect(reverse("account_login"))


def clear_login(request):
    request.session.pop(LOGIN_SESSION_KEY, None)


def unstash_login(request, peek=False):
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
                request._account_login_accessed = True
    return login


def stash_login(request, login):
    request.session[LOGIN_SESSION_KEY] = login.serialize()
    request._account_login_accessed = True
