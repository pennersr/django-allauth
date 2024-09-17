from django.contrib import messages
from django.http import HttpRequest

from allauth.account.internal.stagekit import clear_login


def logout(request: HttpRequest) -> None:
    from allauth.account.adapter import get_adapter

    if request.user.is_authenticated:
        adapter = get_adapter()
        adapter.add_message(
            request, messages.SUCCESS, "account/messages/logged_out.txt"
        )
        adapter.logout(request)
    clear_login(request)
