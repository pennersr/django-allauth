from django.contrib import messages
from django.http import HttpRequest

from allauth.account.internal.flows.password_reset_by_code import (
    PASSWORD_RESET_VERIFICATION_SESSION_KEY,
)
from allauth.account.internal.stagekit import clear_login


def logout(request: HttpRequest, *, show_message: bool = True) -> None:
    from allauth.account.adapter import get_adapter
    from allauth.account.views import INTERNAL_RESET_SESSION_KEY

    if request.user.is_authenticated:
        adapter = get_adapter()
        if show_message:
            adapter.add_message(
                request, messages.SUCCESS, "account/messages/logged_out.txt"
            )
        adapter.logout(request)
    clear_login(request)
    request.session.pop(PASSWORD_RESET_VERIFICATION_SESSION_KEY, None)
    request.session.pop(INTERNAL_RESET_SESSION_KEY, None)
