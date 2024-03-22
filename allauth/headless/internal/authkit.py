from contextlib import contextmanager

from django.conf import settings

from allauth.account.stages import LoginStageController
from allauth.account.utils import unstash_login
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.headless.internal import sessionkit
from allauth.socialaccount.internal import flows


class AuthenticationStatus:
    def __init__(self, request):
        self.request = request

    @property
    def is_authenticated(self):
        return self.request.user.is_authenticated

    def get_stages(self):
        todo = []
        if self.is_authenticated:
            pass
        else:
            login = unstash_login(self.request, peek=True)
            if login:
                ctrl = LoginStageController(self.request, login)
                stages = ctrl.get_stages()
                for stage in stages:
                    if ctrl.is_handled(stage.key):
                        continue
                    todo.append(stage)
                    break
        return todo

    @property
    def has_pending_signup(self):
        return bool(flows.signup.get_pending_signup(self.request))


@contextmanager
def authentication_context(request):
    from allauth.headless.base.response import UnauthorizedResponse

    old_user = request.user
    old_session = request.session
    try:
        request.session = sessionkit.new_session()
        if hasattr(request, "_cached_user"):
            delattr(request, "_cached_user")
        if sessionkit.has_session_token(request):
            session = sessionkit.get_session(request)
            if not session:
                raise ImmediateHttpResponse(UnauthorizedResponse(request, status=410))
            request.session = session
        yield
    finally:
        if request.session.modified:
            request.session.save()
        request.user = old_user
        request.session = old_session
        # e.g. logging in calls csrf `rotate_token()` -- this prevents setting a new CSRF cookie.
        request.META["CSRF_COOKIE_NEEDS_UPDATE"] = False
