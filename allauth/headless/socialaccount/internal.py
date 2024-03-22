from django.http import HttpResponseRedirect

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.core.internal import httpkit
from allauth.headless.internal.authkit import AuthenticationStatus
from allauth.socialaccount.internal import statekit
from allauth.socialaccount.providers.base.constants import AuthError


def on_authentication_error(
    request,
    provider,
    error=None,
    exception=None,
    extra_context=None,
    state_id=None,
):
    """
    Called at a time when it is not clear whether or not this is a headless flow.
    """
    state = None
    if extra_context:
        state = extra_context.get("state")
        if state is None:
            state_id = extra_context.get("state_id")
            if state_id:
                state = statekit.unstash_state(request, state_id)
    if state is None:
        return
    headless = state.get("headless")
    if not headless:
        return
    next_url = state["next"]
    next_url = httpkit.add_query_params(
        next_url, {"error": error, "error_process": state["process"]}
    )
    raise ImmediateHttpResponse(HttpResponseRedirect(next_url))


def complete_social_login(request, sociallogin, func):
    """
    Called when `sociallogin.is_headless`.
    """
    func(request, sociallogin)
    # At this stage, we're either:
    # 1) logged in (or in of the login pipeline stages, such as email verification)
    # 2) auto signed up -- a pipeline stage, so see 1)
    # 3) performing a social signup
    # 4) Stopped, due to not being open-for-signup
    # It would be good to refactor the above into a more generic social login
    # pipeline with clear stages, but for now the /auth endpoint properly responds
    # for cases 1-3.
    next_url = sociallogin.state["next"]
    status = AuthenticationStatus(request)
    if all(
        [
            not status.is_authenticated,
            not status.has_pending_signup,
            not status.get_pending_stage(),
        ]
    ):
        next_url = httpkit.add_query_params(
            next_url,
            {"error": AuthError.UNKNOWN, "error_process": sociallogin.state["process"]},
        )
    return HttpResponseRedirect(next_url)
