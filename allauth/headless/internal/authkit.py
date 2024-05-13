import typing
from contextlib import contextmanager

from allauth import app_settings as allauth_settings
from allauth.account.stages import LoginStageController
from allauth.account.utils import unstash_login
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.headless import app_settings
from allauth.headless.constants import Client
from allauth.headless.internal import sessionkit


class AuthenticationStatus:
    def __init__(self, request):
        self.request = request

    @property
    def is_authenticated(self):
        return self.request.user.is_authenticated

    def get_pending_stage(self):
        stage = None
        if not self.is_authenticated:
            login = unstash_login(self.request, peek=True)
            if login:
                ctrl = LoginStageController(self.request, login)
                stage = ctrl.get_pending_stage()
        return stage

    @property
    def has_pending_signup(self):
        if not allauth_settings.SOCIALACCOUNT_ENABLED:
            return False
        from allauth.socialaccount.internal import flows

        return bool(flows.signup.get_pending_signup(self.request))


def purge_request_user_cache(request):
    if hasattr(request, "_cached_user"):
        delattr(request, "_cached_user")


@contextmanager
def authentication_context(request):
    from allauth.headless.base.response import UnauthorizedResponse

    old_user = request.user
    old_session = request.session
    try:
        request.session = sessionkit.new_session()
        purge_request_user_cache(request)

        strategy = app_settings.TOKEN_STRATEGY
        session_token = strategy.get_session_token(request)
        if session_token:
            session = strategy.lookup_session(session_token)
            if not session:
                raise ImmediateHttpResponse(UnauthorizedResponse(request, status=410))
            request.session = session
            purge_request_user_cache(request)
        request.allauth.headless._pre_user = request.user
        # request.user is lazy -- force evaluation
        request.allauth.headless._pre_user.pk
        yield
    finally:
        if request.session.modified and not request.session.is_empty():
            request.session.save()
        request.user = old_user
        request.session = old_session
        # e.g. logging in calls csrf `rotate_token()` -- this prevents setting a new CSRF cookie.
        request.META["CSRF_COOKIE_NEEDS_UPDATE"] = False


def expose_access_token(request) -> typing.Optional[str]:
    """
    Determines if a new access token needs to be exposed.
    """
    if request.allauth.headless.client != Client.APP:
        return
    if not request.user.is_authenticated:
        return
    pre_user = request.allauth.headless._pre_user
    if pre_user.is_authenticated and pre_user.pk == request.user.pk:
        return
    strategy = app_settings.TOKEN_STRATEGY
    return strategy.create_access_token(request)
