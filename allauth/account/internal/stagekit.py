from typing import Optional

from django.http import HttpResponseRedirect
from django.urls import reverse

from allauth.account.stages import LoginStage, LoginStageController


def get_pending_stage(request) -> Optional[LoginStage]:
    from allauth.account.utils import unstash_login

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
    from allauth.account.internal.flows.login import LOGIN_SESSION_KEY

    request.session.pop(LOGIN_SESSION_KEY, None)
